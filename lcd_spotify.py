"""
Display currently playing Spotify track on LCD.
"""

# SPDX-FileCopyrightText: © 2022, 2024 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

import signal
import sys
import time
from typing import NoReturn

import dotenv

import tools
import extended_lcd
from extended_lcd import ExtendedLcd
from spotify_manager import SpotifyManager

BIPS = 4
CONFIGFILE = "config.env"
WRAP_PAD = " " * 4


class LCD_Spotify:
    """
    Display currently playing Spotify track on LCD.
    """
    def load_config(self):
        """
        Load configuration from config file.
        """
        self.config = {
            "LCD_BACKLIGHT": True,
            "IP_TIMEOUT": 10,
            "I2C_BUS": 1,
            "LCD_ADDRESS": 0x27,
            "LCD_WIDTH": 16,
            "LCD_ROWS": 2,
            **dotenv.dotenv_values(dotenv_path=CONFIGFILE) # load config overrides
        }
        # convert from string to proper type for config values
        self.config["LCD_BACKLIGHT"] = tools.str_to_bool(self.config["LCD_BACKLIGHT"], True)
        self.config["IP_TIMEOUT"] = int(self.config["IP_TIMEOUT"])
        self.config["LCD_ADDRESS"] = int(self.config["LCD_ADDRESS"], 16)
        self.config["I2C_BUS"] = int(self.config["I2C_BUS"])
        self.config["LCD_WIDTH"] = int(self.config["LCD_WIDTH"])
        self.config["LCD_ROWS"] = int(self.config["LCD_ROWS"])

    def init_hardware(self):
        """
        Initialize the LCD.
        """
        self.lcd = ExtendedLcd(
            address=self.config["LCD_ADDRESS"],
            bus=self.config["I2C_BUS"],
            width=self.config["LCD_WIDTH"],
            rows=self.config["LCD_ROWS"],
            backlight=self.config["LCD_BACKLIGHT"]
        )
        self.lcd.save_cgram_char(
            slot=extended_lcd.CGRAM_SLOT1,
            bytedata=extended_lcd.CHR_HEART
        )

    def init_spotify(self):
        """
        Initialize Spotify Web API.
        """
        self.spotify_manager = SpotifyManager(
            client_id=self.config["SPOTIPY_CLIENT_ID"],
            client_secret=self.config["SPOTIPY_CLIENT_SECRET"],
            redirect_uri=self.config["SPOTIPY_REDIRECT_URI"],
        )

    def __init__(self):
        self.load_config()
        self.init_hardware()
        self.init_spotify()
        self.countdown = 0
        self.bip = 0
        self.offsets = {
            "album": 0,
            "artist": 0,
            "track": 0,
        }

    def reset_countdown(self):
        """
        Reset the countdown timer.
        """
        self.countdown = time.time()

    def increment_display_offsets(self):
        """
        Return the offset numbers for the display data.
        """
        if self.spotify_manager.update_last_track():
            tools.eprint(
                self.spotify_manager.get_artist(),
                self.spotify_manager.get_track_name(),
                self.spotify_manager.get_album_name(),
                sep="::"
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
        Wrapper to substr_wrap using LCD width for max length.
        """
        return tools.substr_wrap(string, offset, self.lcd.width, WRAP_PAD)

    def single_step(self):
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
        if time.time() - self.countdown < self.config["IP_TIMEOUT"]:
            self.lcd.text(f"HOST: {tools.gethostname()}", 1, "center")
            self.lcd.text(f"IP: {tools.net_addr()}", 2, "center")
        elif self.spotify_manager.is_track_playing():
            if self.spotify_manager.is_track_liked():
                artist_display = extended_lcd.CGRAM_CHR1 + self.spotify_manager.get_artist()
            else:
                artist_display = self.spotify_manager.get_artist()
            self.increment_display_offsets()
            artist = self.offset_wrap(artist_display, self.offsets["artist"])
            track = self.offset_wrap(self.spotify_manager.get_track_name(), self.offsets["track"])
            album = self.offset_wrap(self.spotify_manager.get_album_name(), self.offsets["album"])
            self.lcd.position_text(artist.ljust(self.lcd.width), 1)
            self.lcd.position_text(track.ljust(self.lcd.width), 2)
            if self.lcd.rows > 2:
                self.lcd.position_text(album.ljust(self.lcd.width), 3)
        else:
            self.lcd.text(time.strftime('%H:%M:%S'), 1, "center")
            self.lcd.text(time.strftime('%Y-%m-%d'), 2, "center")


def main() -> NoReturn:
    """
    Entry point function when run from command line.
    """
    def signal_handler(*args):
        """
        Handle various signals
        """
        signum = args[0]
        tools.eprint(f'Handling signal {signum} ({signal.Signals(signum).name}).')
        if signum == signal.SIGUSR1:
            lcd_spotify.lcd.toggle_backlight()
        elif signum == signal.SIGUSR2:
            lcd_spotify.spotify_manager.toggle_track_liked()
        elif signum == signal.SIGIO:
            lcd_spotify.reset_countdown()
        elif signum == signal.SIGALRM:
            lcd_spotify.spotify_manager.next_track()
        elif signum in (signal.SIGINT, signal.SIGTERM):
            lcd_spotify.lcd.clear()
            sys.exit(0)
        else:
            tools.eprint("Unknown signal received.")

    lcd_spotify = LCD_Spotify()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)
    signal.signal(signal.SIGIO, signal_handler)
    signal.signal(signal.SIGALRM, signal_handler)
    while True:
        lcd_spotify.single_step()
        time.sleep(1 / BIPS)


if __name__ == '__main__':
    main()
