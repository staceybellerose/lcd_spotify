"""
Spotify API Manager.
"""

# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import dataclasses
import logging

import requests
import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

CACHEFILE = ".cache-spotipy"
SPOTIFY_SCOPE = " ".join(  # noqa: FLY002
    [
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-library-read",
        "user-library-modify"
    ]
)

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TrackData:
    """
    Track Information.
    """

    id: str
    name: str
    album: str
    artist: str
    is_playing: bool
    is_liked: bool

    def __eq__(self, other: object) -> bool:
        if other is self:
            return True
        if isinstance(other, self.__class__):
            return (
                self.id == other.id
                and self.name == other.name
                and self.album == other.album
                and self.artist == other.artist
            )
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class SpotifyManager:
    """
    Spotify API Manager.
    """

    def __init__(
        self, client_id: str | None = None, client_secret: str | None = None,
        redirect_uri: str | None = None
    ) -> None:
        self.cfh = CacheFileHandler(cache_path=CACHEFILE)
        self.spo = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SPOTIFY_SCOPE,
            open_browser=False,
            cache_handler=self.cfh
        )
        self.sp = spotipy.Spotify(
            auth_manager=self.spo
        )
        self.current_track: TrackData | None = None
        self.last_track: TrackData | None = None

    def next_track(self) -> None:
        """
        Advance to the next track, if currently playing something.
        """
        if self.current_track and self.current_track.is_playing:
            try:
                logger.info("Advancing to next track")
                self.sp.next_track()
            except requests.exceptions.Timeout:
                logger.warning("Spotify call (next_track) timed out")

    def toggle_track_liked(self) -> None:
        """
        Toggle the Track Likes flag on Spotify.
        """
        if self.current_track and self.current_track.is_playing:
            try:
                logger.info("Toggling whether track is liked")
                if self.current_track.is_liked:
                    self.sp.current_user_saved_tracks_delete([self.current_track.id])
                else:
                    self.sp.current_user_saved_tracks_add([self.current_track.id])
            except requests.exceptions.Timeout:
                logger.warning("Spotify call (current_user_saved_tracks_add/delete) timed out")

    def retrieve_track_data(self) -> None:
        """
        Retrieve currently playing track from Spotify.
        """
        try:
            logger.debug("Retrieving track data from Spotify")
            track = self.sp.current_user_playing_track()
            if track is not None:
                track_details = track["item"]
                track_id = track_details["id"]
                artist_name, album_name = self._get_artist_and_album_from_track(track)
                track_liked = self._ask_spotify_if_track_liked(track_id)
                self.current_track = TrackData(
                    track_id,
                    track_details["name"],
                    album_name,
                    artist_name,
                    track["is_playing"],
                    track_liked
                )
            else:
                self.current_track = None
        except requests.exceptions.Timeout:
            logger.warning("Spotify call (current_user_playing_track) timed out")

    def _get_artist_and_album_from_track(self, track: dict) -> tuple[str, str]:
        track_details = track["item"]
        if track["currently_playing_type"] == "track":
            artists = [artist["name"] for artist in track_details["artists"]]
            artist_name = ", ".join(artists)
            album_name = track_details["album"]["name"]
        elif track["currently_playing_type"] == "episode":
            artist_name = track_details["show"]["publisher"]
            album_name = track_details["show"]["episode"]
        else:
            artist_name = ""
            album_name = ""
        return (artist_name, album_name)

    def _ask_spotify_if_track_liked(self, track_id: str) -> bool:
        """
        Determine is Spotify believes the current track is liked.
        """
        try:
            logger.debug("Retrieving if track liked from Spotify")
            return self.sp.current_user_saved_tracks_contains([track_id])[0]
        except requests.exceptions.Timeout:
            logger.warning("Spotify call (current_user_saved_tracks_contains) timed out")
            return False

    def get_artist(self) -> str:
        """
        Get the current track's artist name.
        """
        return self.current_track.artist if self.current_track is not None else ""

    def get_album_name(self) -> str:
        """
        Get the current track's album name.
        """
        return self.current_track.album if self.current_track is not None else ""

    def get_track_name(self) -> str:
        """
        Get the current track's name.
        """
        return self.current_track.name if self.current_track is not None else ""

    def is_track_liked(self) -> bool:
        """
        Determine if the current track is liked.
        """
        return self.current_track.is_liked if self.current_track is not None else False

    def is_track_playing(self) -> bool:
        """
        Determine if the current track is actually playing.
        """
        return self.current_track is not None and self.current_track.is_playing

    def update_last_track(self) -> bool:
        """
        If the last track is not the current track, update last track.

        Returns True if last track was updated.
        """
        if (flag := self.last_track != self.current_track):
            self.last_track = self.current_track
        return flag
