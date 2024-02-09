"""
Spotify API Manager.
"""

# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

import dataclasses

import requests
import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

import tools

CACHEFILE = ".cache-spotipy"
SPOTIFY_SCOPE = " ".join(
    [
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-library-read",
        "user-library-modify"
    ]
)


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


class SpotifyManager():
    """
    Spotify API Manager.
    """
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=SPOTIFY_SCOPE,
                open_browser=False,
                cache_handler=CacheFileHandler(cache_path=CACHEFILE)
            )
        )
        self.current_track: TrackData = None
        self.last_track: TrackData = None

    def next_track(self):
        """
        Advance to the next track, if currently playing something.
        """
        if self.current_track.is_playing:
            self.sp.next_track()

    def toggle_track_liked(self):
        """
        Toggle the Track Likes flag on Spotify.
        """
        if self.current_track.is_playing:
            if self.current_track.is_liked:
                self.sp.current_user_saved_tracks_delete([self.current_track.id])
            else:
                self.sp.current_user_saved_tracks_add([self.current_track.id])

    def retrieve_track_data(self):
        """
        Retrieve currently playing track from Spotify.
        """
        try:
            track = self.sp.current_user_playing_track()
            if track is not None:
                track_details = track["item"]
                track_id = track_details["id"]
                if track["currently_playing_type"] == "track":
                    artists = [artist["name"] for artist in track_details["artists"]]
                    artist_name = ', '.join(artists)
                    album_name = track_details["album"]["name"]
                elif track["currently_playing_type"] == "episode":
                    artist_name = track_details["show"]["publisher"]
                    album_name = track_details["show"]["episode"]
                if self.current_track is not None and self.current_track.is_playing:
                    track_liked = self._ask_spotify_if_track_liked(track_id)
                else:
                    track_liked = False
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
        except requests.exceptions.RequestException:
            tools.dump_traceback("Warning: Spotify call timed out")

    def _ask_spotify_if_track_liked(self, track_id: str) -> bool:
        """
        Determine is Spotify believes the current track is liked.
        """
        return self.sp.current_user_saved_tracks_contains([track_id])[0]

    def get_artist(self) -> str:
        """
        Get the current track's artist name.
        """
        return self.current_track.artist

    def get_album_name(self) -> str:
        """
        Get the current track's album name.
        """
        return self.current_track.album

    def get_track_name(self) -> str:
        """
        Get the current track's name.
        """
        return self.current_track.name

    def is_track_liked(self) -> bool:
        """
        Determine if the current track is liked.
        """
        return self.current_track.is_liked

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
