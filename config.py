"""
Configuration management.
"""

# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import dataclasses
from typing import Any

import dotenv
from typing_extensions import Self


class IntConversionDescriptor:
    """Integer conversion descriptor object."""

    def __init__(self, *, default: int) -> None:
        self._default = default
        self._name = "_int"

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = f"_{owner.__name__}_{name}"

    def __get__(self, obj: object, _type: type) -> int:
        if obj is None:
            return self._default

        return getattr(obj, self._name, self._default)

    def __set__(self, obj: object, value: Any) -> None:  # noqa: ANN401
        base = 10
        if isinstance(value, str):
            if value[:2] == "0x":
                base = 16
            if value[:2] == "0o":
                base = 8
            if value[:2] == "0b":
                base = 2
        setattr(obj, self._name, int(value, base))


class BoolConversionDescriptor:
    """Boolean conversion descriptor object."""

    def __init__(self, *, default: bool) -> None:
        self._default = default
        self._name = "_bool"

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = f"_{owner.__name__}_{name}"

    def __get__(self, obj: object, _type: type) -> bool:
        if obj is None:
            return self._default

        return getattr(obj, self._name, self._default)

    def __set__(self, obj: object, value: Any) -> None:  # noqa: ANN401
        val = bool(value)
        if isinstance(value, str):
            value = value.lower()
        if value in ["y", "yes", "t", "true", "on", "1", 1]:
            val = True
        elif value in ["n", "no", "f", "false", "off", "0", 0]:
            val = False
        setattr(obj, self._name, val)


@dataclasses.dataclass
class Config:  # pylint: disable=too-many-instance-attributes
    """Data configuration."""

    lcd_backlight: BoolConversionDescriptor = BoolConversionDescriptor(default=True)
    ip_timeout: IntConversionDescriptor = IntConversionDescriptor(default=10)
    i2c_bus: IntConversionDescriptor = IntConversionDescriptor(default=1)
    lcd_address: IntConversionDescriptor = IntConversionDescriptor(default=0x27)
    lcd_width: IntConversionDescriptor = IntConversionDescriptor(default=16)
    lcd_rows: IntConversionDescriptor = IntConversionDescriptor(default=2)
    spotipy_client_id: str | None = None
    spotipy_client_secret: str | None = None
    spotipy_redirect_uri: str | None = None

    @classmethod
    def load_from_file(cls, filename: str) -> Self:
        """Create a Config instance, loading data from a file."""
        dotenv_config = dotenv.dotenv_values(dotenv_path=filename)
        return cls(
            lcd_backlight=dotenv_config["LCD_BACKLIGHT"],
            ip_timeout=dotenv_config["IP_TIMEOUT"],
            i2c_bus=dotenv_config["I2C_BUS"],
            lcd_address=dotenv_config["LCD_ADDRESS"],
            lcd_width=dotenv_config["LCD_WIDTH"],
            lcd_rows=dotenv_config["LCD_ROWS"],
            spotipy_client_id=dotenv_config["SPOTIPY_CLIENT_ID"],
            spotipy_client_secret=dotenv_config["SPOTIPY_CLIENT_SECRET"],
            spotipy_redirect_uri=dotenv_config["SPOTIPY_REDIRECT_URI"]
        )
