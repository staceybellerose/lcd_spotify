"""
Log handling classes.
"""

# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging


class LogFilter(logging.Filterer):
    """
    Custom filtering for logging facility.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter the log record."""
        if record.name.startswith("spotipy"):
            return False
        if record.name.startswith("urllib3"):
            return False
        # if record.levelno > logging.DEBUG:
        #     return False
        return True


class LogFormatter(logging.Formatter):
    """
    Custom formatting for logging facility.
    """

    def __init__(self) -> None:
        super().__init__()
        self.default_format = "%(levelname)s:%(name)s:%(message)s"

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record.
        """
        log_fmt = "%(message)s" if record.levelno == logging.INFO else self.default_format
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
