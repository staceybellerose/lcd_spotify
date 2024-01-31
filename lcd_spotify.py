"""
Display currently playing Spotify track on LCD.
"""

# SPDX-FileCopyrightText: © 2022, 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

import dataclasses
import os
import signal
import socket
import sys
import time
import traceback

import dotenv
import psutil
import requests
import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

import extended_lcd
from eprint import eprint
from extended_lcd import ExtendedLcd

CONFIGFILE = "config.env"
CACHEFILE = ".cache-spotipy"
WRAP_PAD = " " * 4
SPOTIFY_SCOPE = "user-read-playback-state user-modify-playback-state user-library-read user-library-modify"


@dataclasses.dataclass
class SpotifyConfig:
    """
    Spotify Web API Configuration.
    """
    spotipy_client_id: str
    spotipy_client_secret: str
    spotipy_redirect_uri: str


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


class LCD_Spotify:
    """
    Display currently playing Spotify track on LCD.
    """
    def load_env(self):
        """
        Load configuration from environment.
        """
        self.backlight = self.str_to_bool(os.getenv("LCD_BACKLIGHT", "True"), True)
        self.timeout = int(os.getenv("IP_TIMEOUT", "10"))
        self.spotipy_config = SpotifyConfig(
            spotipy_client_id = os.getenv("SPOTIPY_CLIENT_ID"),
            spotipy_client_secret = os.getenv("SPOTIPY_CLIENT_SECRET"),
            spotipy_redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
        )
        if self.spotipy_config.spotipy_client_id is None:
            raise ValueError("Missing SPOTIPY_CLIENT_ID environment variable")
        if self.spotipy_config.spotipy_client_secret is None:
            raise ValueError("Missing SPOTIPY_CLIENT_SECRET environment variable")
        if self.spotipy_config.spotipy_redirect_uri is None:
            raise ValueError("Missing SPOTIPY_REDIRECT_URI environment variable")

    def init_hardware(self):
        """
        Initialize the LCD.
        """
        self.lcd = ExtendedLcd(
            address=int(os.getenv("LCD_ADDRESS", "0x27"), 16),
            bus=int(os.getenv("I2C_BUS", "1")),
            width=int(os.getenv("LCD_WIDTH", "16")),
            rows=int(os.getenv("LCD_ROWS", "2")),
            backlight=self.backlight
        )
        self.lcd.save_cgram_char(extended_lcd.CGRAM_SLOT1, extended_lcd.CHR_HEART)

    def init_spotify(self):
        """
        Initialize Spotify Web API.
        """
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope=SPOTIFY_SCOPE,
                open_browser=False,
                cache_handler=CacheFileHandler(cache_path=CACHEFILE)
            )
        )

    def __init__(self):
        self.BIPS = 4
        self.backlight = True
        self.countdown = 0
        self.bip = 0
        dotenv.load_dotenv(dotenv_path = CONFIGFILE)
        self.load_env()
        self.init_hardware()
        self.init_spotify()
        self.current_track = None
        self.last_track = None

    def str_to_bool(self, val, default=False):
        """Convert a string representation of truth to True or False.
        True values are 'y', 'yes', 't', 'true', 'on', and '1'.
        False values are 'n', 'no', 'f', 'false', 'off', and '0'.
        Returns default if 'val' is anything else.
        """
        val = val.lower()
        if val in ('y', 'yes', 't', 'true', 'on', '1'):
            return True
        if val in ('n', 'no', 'f', 'false', 'off', '0'):
            return False
        return bool(default)

    def net_addr(self):
        """
        Retrieve the IPv4 address of the first non-loopback adapter.
        Returns empty string if none found.
        """
        addresses = psutil.net_if_addrs()
        for key, addresslist in addresses.items():
            if key != "lo":
                for addr in addresslist:
                    if addr.family == socket.AF_INET:
                        return addr.address
        return ""

    def add_to_max(self, add1, add2, max_num):
        """
        Add two numbers, and wrap to max
        """
        return (add1 + add2) % max_num

    def substr_wrap(self, string, start, length, wrap_pad = ""):
        """
        Create a substring which starts at a given position, and extends
        for lenght characters, wrapping if the end of string is reached.

        Examples:
            print(substr_wrap("0123456789", 7, 5))
            => 78901

            print(substr_wrap("0123456789", 8, 5, " "))
            => 890 1
        """
        if len(string) <= length:
            return string
        string = string + wrap_pad
        chrs = [string[self.add_to_max(start, i, len(string))] for i in range(length)]
        return "".join(chrs)

    def toggle_backlight(self):
        """
        Toggle the backlight on the LCD.
        """
        self.backlight = not self.backlight
        self.lcd.backlight(self.backlight)

    def toggle_track_liked(self):
        """
        Toggle the Track Likes flag on Spotify
        """
        if self.current_track.is_playing:
            if self.current_track.is_liked:
                self.sp.current_user_saved_tracks_delete([self.current_track.id])
            else:
                self.sp.current_user_saved_tracks_add([self.current_track.id])

    def clear_lcd(self):
        """
        Clear the LCD and turn off the backlight.
        """
        self.lcd.clear()
        self.lcd.backlight(False)

    def reset_countdown(self):
        """
        Reset the countdown timer.
        """
        self.countdown = time.time()

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
                    artist_names = track_details["artists"]
                    artists = []
                    for artist in artist_names:
                        artists.append(artist["name"])
                    artist_name = ', '.join(artists)
                    album_name = track_details["album"]["name"]
                elif track["currently_playing_type"] == "episode":
                    artist_name = track_details["show"]["publisher"]
                    album_name = track_details["show"]["episode"]
                if track["is_playing"]:
                    track_liked = self.sp.current_user_saved_tracks_contains([track_id])[0]
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
            eprint(traceback.format_exc())
            eprint("Warning: Spotify call timed out")

    def offset_display_data(self):
        """
        Return the offset numbers for the display data.
        """
        if self.last_track != self.current_track:
            eprint(
                f"{self.current_track.artist}::{self.current_track.name}::{self.current_track.album}"
            )
            self.last_track = self.current_track
            offset_artist = 0
            offset_track = 0
            offset_album = 0
        else:
            offset_artist = self.add_to_max(
                offset_artist, 1,
                len(self.current_track.artist) + len(WRAP_PAD)
            )
            offset_track = self.add_to_max(
                offset_track, 1,
                len(self.current_track.name) + len(WRAP_PAD)
            )
            offset_album = self.add_to_max(
                offset_album, 1,
                len(self.current_track.album) + len(WRAP_PAD)
            )
        return (offset_artist, offset_track, offset_album)

    def offset_wrap(self, string, offset):
        """
        Wrapper to substr_wrap using default values for LCD
        """
        return self.substr_wrap(string, offset, self.lcd.width, WRAP_PAD)

    def single_step(self):
        """
        Single Step of display:
            Get current Spotify track.
            Display track information on LCD.
        """
        if self.bip == 0:
            self.retrieve_track_data()
        self.bip = (self.bip + 1) % self.BIPS
        if time.time() - self.countdown < self.timeout:
            self.lcd.text(f"HOST: {socket.gethostname()}", 1)
            self.lcd.text(f"IP: {self.net_addr()}", 2)
        elif self.current_track is not None and self.current_track.is_playing:
            if self.current_track.is_liked:
                artist_display = extended_lcd.CGRAM_CHR1 + self.current_track.artist
            else:
                artist_display = self.current_track.artist
            (offset_artist, offset_track, offset_album) = self.offset_display_data()
            artist = self.offset_wrap(artist_display, offset_artist)
            track = self.offset_wrap(self.current_track.name, offset_track)
            album = self.offset_wrap(self.current_track.album, offset_album)
            self.lcd.text(artist, 1)
            self.lcd.text(track, 2)
            if self.lcd.rows > 2:
                self.lcd.text(album, 3)
        else:
            self.lcd.text(f"    {time.strftime('%H:%M:%S')}   ", 1)
            self.lcd.text(f"   {time.strftime('%Y-%m-%d')}   ", 2)


def signal_handler(signum, _frame):
    """
    Handle various signals
    """
    eprint(f'Handling signal {signum} ({signal.Signals(signum).name}).')
    if signum == signal.SIGUSR1:
        lcd_spotify.toggle_backlight()
    elif signum == signal.SIGUSR2:
        lcd_spotify.toggle_track_liked()
    elif signum == signal.SIGIO:
        lcd_spotify.reset_countdown()
    elif signum == signal.SIGINT:
        lcd_spotify.clear_lcd()
        sys.exit(0)
    else:
        eprint("Unknown signal received.")


lcd_spotify = LCD_Spotify()
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)
    signal.signal(signal.SIGIO, signal_handler)
    while True:
        lcd_spotify.single_step()
        time.sleep(1 / lcd_spotify.BIPS)
