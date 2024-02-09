#!/usr/bin/env python3

"""
Prototype showing how to connect to spotify and retrieve the currently playing track.
"""

# SPDX-FileCopyrightText: © 2022 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

import dotenv
import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

CACHEFILE = "../.cache-spotipy"

dotenv.load_dotenv(dotenv_path = "../config.env")

scope = "user-read-playback-state user-library-read"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        open_browser=False,
        cache_handler=CacheFileHandler(cache_path=CACHEFILE)
    )
)

track = sp.current_user_playing_track()
if track is not None:
    track_details = track["item"]
    if track["is_playing"]:
        print("Artist:", track_details["artists"][0]["name"])
        print("Song:", track_details["name"])
        print("Spotify ID:", track_details["id"])
        liked = sp.current_user_saved_tracks_contains([track_details["id"]])
        if liked[0]:
            print("♥ Liked!")
        else:
            print("not liked")
    else:
        print("No track currently playing")
else:
    print("No track currently playing")
