"""
Display currently playing Spotify track on LCD.
"""

# SPDX-FileCopyrightText: © 2022, 2024 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import time
from contextlib import suppress

import extended_lcd
import tools
from config import Config
from extended_lcd import ExtendedLcd
from spotify_manager import SpotifyManager

BIPS = 4
CONFIGFILE = "config.env"
WRAP_PAD = " " * 4

logger = logging.getLogger(__name__)


class LcdSpotify:
    """
    Display currently playing Spotify track on LCD.
    """

    def load_config(self) -> None:
        """
        Load configuration from config file.
        """
        self.config = Config.load_from_file(CONFIGFILE)
        logger.debug("Loaded config: %s", self.config)

    def init_hardware(self) -> None:
        """
        Initialize the LCD.
        """
        self.lcd = ExtendedLcd(
            address=self.config.lcd_address,
            bus=self.config.i2c_bus,
            width=self.config.lcd_width,
            rows=self.config.lcd_rows,
            backlight=self.config.lcd_backlight
        )
        self.lcd.save_cgram_char(
            slot=extended_lcd.CGRAM_SLOT1,
            bytedata=extended_lcd.CHR_HEART
        )
        logger.debug("LCD initialized: %s", self.lcd)

    def init_spotify(self) -> None:
        """
        Initialize Spotify Web API.
        """
        self.spotify_manager = SpotifyManager(
            client_id=self.config.spotipy_client_id,
            client_secret=self.config.spotipy_client_secret,
            redirect_uri=self.config.spotipy_redirect_uri,
        )
        logger.debug("Spotify API initialized")

    def __init__(self) -> None:
        self.load_config()
        self.init_hardware()
        self.init_spotify()
        self.countdown = 0.0
        self.bip = 0
        self.offsets = {
            "album": 0,
            "artist": 0,
            "track": 0,
        }

    def reset_countdown(self) -> None:
        """
        Reset the countdown timer.
        """
        self.countdown = time.time()

    def increment_display_offsets(self) -> None:
        """
        Return the offset numbers for the display data.
        """
        if self.spotify_manager.update_last_track():
            logger.info(
                "%s::%s::%s",
                self.spotify_manager.get_artist(),
                self.spotify_manager.get_track_name(),
                self.spotify_manager.get_album_name(),
            )
            self.offsets["artist"] = 0
            self.offsets["album"] = 0
            self.offsets["track"] = 0
        else:
            self.offsets["artist"] = tools.add_to_max(
                self.offsets["artist"], 1,
                len(self.spotify_manager.get_artist()) + len(WRAP_PAD)
            )
            self.offsets["track"] = tools.add_to_max(
                self.offsets["track"], 1,
                len(self.spotify_manager.get_track_name()) + len(WRAP_PAD)
            )
            self.offsets["album"] = tools.add_to_max(
                self.offsets["album"], 1,
                len(self.spotify_manager.get_album_name()) + len(WRAP_PAD)
            )

    def offset_wrap(self, string: str, offset: int) -> str:
        """
        Wrap a string with a given offset, to fit the LCD width.
        """
        return tools.substr_wrap(string, offset, self.lcd.width, WRAP_PAD)

    def _get_liked_artist(self, artist_name: str) -> str:
        if self.spotify_manager.is_track_liked():
            return extended_lcd.CGRAM_CHR1 + artist_name
        return artist_name

    def single_step(self) -> None:
        """
        Run a single step of display loop.

        Get currently playing Spotify track, then display information on LCD:
            * If user requested host/IP address, display it for IP_TIMEOUT seconds.
            * If Spotify is currently playing, display track information.
            * Otherwise, display current time and date.
        """
        if self.bip == 0:
            self.spotify_manager.retrieve_track_data()
        self.bip = (self.bip + 1) % BIPS
        if time.time() - self.countdown < self.config.ip_timeout:
            self.lcd.text(f"HOST: {tools.gethostname()}", 1, "center")
            self.lcd.text(f"IP: {tools.net_addr()}", 2, "center")
        elif self.spotify_manager.is_track_playing():
            artist_name = tools.remove_diacritics(self.spotify_manager.get_artist())
            artist_display = self._get_liked_artist(artist_name)
            self.increment_display_offsets()
            artist = self.offset_wrap(artist_display, self.offsets["artist"])
            track = self.offset_wrap(
                tools.remove_diacritics(
                    self.spotify_manager.get_track_name()
                ), self.offsets["track"]
            )
            album = self.offset_wrap(
                tools.remove_diacritics(
                    self.spotify_manager.get_album_name()
                ), self.offsets["album"]
            )
            with suppress(ValueError):
                self.lcd.position_text(artist.ljust(self.lcd.width), 1)
                self.lcd.position_text(track.ljust(self.lcd.width), 2)
                # a 16x2 LCD will throw a ValueError here, but a 20x4 won't
                self.lcd.position_text(album.ljust(self.lcd.width), 3)
        else:
            self.lcd.text(time.strftime("%H:%M:%S"), 1, "center")
            self.lcd.text(time.strftime("%Y-%m-%d"), 2, "center")
