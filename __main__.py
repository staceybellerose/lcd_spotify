"""
Main entry for program.
"""

# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

import logging
import signal
import sys
import time

from requests.exceptions import RequestException
from spotipy.exceptions import SpotifyException

from lcd_spotify import LcdSpotify
from log_handling import LogFilter, LogFormatter


def clear_lcd_and_exit() -> None:
    """Clear the LCD and exit the program."""
    lcd_spotify.lcd.clear()
    sys.exit(0)


def signal_handler(*args) -> None:
    """Handle various signals."""
    signum = args[0]
    logger.info("Handling signal %s (%s)", signum, signal.Signals(signum).name)
    sig_options = {
        signal.SIGUSR1: lcd_spotify.lcd.toggle_backlight,
        signal.SIGUSR2: lcd_spotify.spotify_manager.toggle_track_liked,
        signal.SIGIO: lcd_spotify.reset_countdown,
        signal.SIGALRM: lcd_spotify.spotify_manager.next_track,
        signal.SIGHUP: clear_lcd_and_exit,
        signal.SIGINT: clear_lcd_and_exit,
        signal.SIGTERM: clear_lcd_and_exit,
    }
    try:
        sig_options[signum]()  # use dict to simulate switch
    except IndexError:
        logger.warning("Unknown signal received.")


def init_logger(lgr: logging.Logger) -> None:
    """Initialize the logging facility."""
    lgr.setLevel(logging.DEBUG)
    error_console = logging.StreamHandler(sys.stderr)
    error_console.addFilter(LogFilter())
    error_console.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    output_console = logging.StreamHandler(sys.stdout)
    output_console.setLevel(logging.INFO)
    output_console.setFormatter(LogFormatter())
    lgr.addHandler(error_console)
    lgr.addHandler(output_console)


def init_signals() -> None:
    """Initialize signal handlers."""
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGUSR2, signal_handler)
    signal.signal(signal.SIGIO, signal_handler)
    signal.signal(signal.SIGALRM, signal_handler)


if __name__ == "__main__":
    logger = logging.getLogger("root")
    lcd_spotify = LcdSpotify()
    init_logger(logger)
    init_signals()
    while True:
        try:
            lcd_spotify.single_step()
        except SpotifyException:
            logger.exception("Spotify exception occurred")
            clear_lcd_and_exit()
        except RequestException:
            logger.exception("Requests library exception occurred")
            clear_lcd_and_exit()
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Unknown exception occurred")
            clear_lcd_and_exit()
        time.sleep(0.5)  # 0.5 seconds between lcd refreshes
