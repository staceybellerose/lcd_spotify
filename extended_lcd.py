"""
Extended LCD class with convenience functions.
"""

# SPDX-FileCopyrightText: © 2022 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from rpi_lcd import LCD, LINES

# Valid character positions
CGRAM_SLOT1 = 0
CGRAM_SLOT2 = 1
CGRAM_SLOT3 = 2
CGRAM_SLOT4 = 3
CGRAM_SLOT5 = 4
CGRAM_SLOT6 = 5
CGRAM_SLOT7 = 6
CGRAM_SLOT8 = 7

# Character codes for CGRAM slots
CGRAM_CHR1 = chr(0)
CGRAM_CHR2 = chr(1)
CGRAM_CHR3 = chr(2)
CGRAM_CHR4 = chr(3)
CGRAM_CHR5 = chr(4)
CGRAM_CHR6 = chr(5)
CGRAM_CHR7 = chr(6)
CGRAM_CHR8 = chr(7)

# Custom characters available to load into LCD's CGRAM
# Note that LCDs using the Hitachi HD44780 controller only allow for 8 custom characters

CHR_HEART      = [0b00000, 0b01010, 0b11111, 0b11111, 0b01110, 0b00100, 0b00000, 0b00000]
CHR_BELL       = [0b00100, 0b01110, 0b01110, 0b01110, 0b11111, 0b00000, 0b00100, 0b00000]
CHR_CHECK      = [0b00000, 0b00001, 0b00011, 0b10110, 0b11100, 0b01000, 0b00000, 0b00000]
CHR_SPEAKER    = [0b00001, 0b00011, 0b01111, 0b01111, 0b01111, 0b00011, 0b00001, 0b00000]
CHR_MUSIC      = [0b00001, 0b00011, 0b00101, 0b01001, 0b01001, 0b01011, 0b11011, 0b11000]
CHR_SKULL      = [0b00000, 0b01110, 0b10101, 0b11011, 0b01110, 0b01110, 0b00000, 0b00000]
CHR_LOCK       = [0b01110, 0b10001, 0b10001, 0b11111, 0b11011, 0b11011, 0b11111, 0b00000]
CHR_UNLOCK     = [0b01110, 0b10000, 0b10000, 0b11111, 0b11011, 0b11011, 0b11111, 0b00000]
CHR_UPARROW    = [0b00100, 0b01110, 0b10101, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000]
CHR_DOWNARROW  = [0b00000, 0b00100, 0b00100, 0b00100, 0b00100, 0b10101, 0b01110, 0b00100]
CHR_RIGHTARROW = [0b00000, 0b00100, 0b00010, 0b11111, 0b00010, 0b00100, 0b00000, 0b00000]
CHR_LEFTARROW  = [0b00000, 0b00100, 0b01000, 0b11111, 0b01000, 0b00100, 0b00000, 0b00000]
CHR_DEGREE     = [0b01100, 0b10010, 0b10010, 0b01100, 0b00000, 0b00000, 0b00000, 0b00000]
CHR_LOOP       = [0b01110, 0b10001, 0b10001, 0b10101, 0b00110, 0b00111, 0b00000, 0b00000]
CHR_PLAY       = [0b01000, 0b01100, 0b01110, 0b01111, 0b01110, 0b01100, 0b01000, 0b00000]
CHR_PAUSE      = [0b00000, 0b11011, 0b11011, 0b11011, 0b11011, 0b11011, 0b11011, 0b00000]
CHR_STOP       = [0b00000, 0b01110, 0b01110, 0b01110, 0b01110, 0b01110, 0b01110, 0b00000]
CHR_SOUNDON    = [0b01000, 0b00100, 0b10010, 0b01010, 0b01010, 0b10010, 0b00100, 0b01000]
CHR_SOUNDOFF   = [0b10001, 0b11011, 0b01110, 0b00100, 0b01110, 0b11011, 0b10001, 0b00000]
CHR_BATTERY0   = [0b01110, 0b11011, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11111]
CHR_BATTERY1   = [0b01110, 0b11011, 0b10001, 0b10001, 0b10001, 0b10001, 0b11111, 0b11111]
CHR_BATTERY2   = [0b01110, 0b11011, 0b10001, 0b10001, 0b10001, 0b11111, 0b11111, 0b11111]
CHR_BATTERY3   = [0b01110, 0b11011, 0b10001, 0b10001, 0b11111, 0b11111, 0b11111, 0b11111]
CHR_BATTERY4   = [0b01110, 0b11011, 0b10001, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111]
CHR_BATTERY5   = [0b01110, 0b11011, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111]
CHR_BATTERY6   = [0b01110, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111]
CHR_FN         = [0b11100, 0b10000, 0b11100, 0b10000, 0b10110, 0b00101, 0b00101, 0b00000]
CHR_ROSETTE    = [0b11011, 0b10101, 0b10101, 0b01110, 0b01110, 0b10101, 0b10101, 0b11011]

# REDEFINED CHARACTERS FROM ASCII

# the ASCII code for backslash is used to display Yen
CHR_BACKSLASH  = [0b00000, 0b10000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00000, 0b00000]
# the ASCII code for tilde is used to display left arrow
CHR_TILDE      = [0b00000, 0b01101, 0b10011, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000]

# ALIASES

CHR_BATTERY_EMPTY = CHR_BATTERY0
CHR_BATTERY_HALF  = CHR_BATTERY3
CHR_BATTERY_FULL  = CHR_BATTERY6

# more custom characters can be designed at https://maxpromer.github.io/LCD-Character-Creator/

CHR_DATA_LENGTH = 8


class ExtendedLcd(LCD):
    """
    Extended LCD class with convenience functions.
    """

    def save_cgram_char(self, slot: int, bytedata: list[int]) -> None:
        """
        Load bytedata into LCD's CGRAM.

        Parameters
        ----------
        slot: An integer between 0 and 7, inclusive
        bytedata: A list of 8 bytes with values between 0x00 and 0x1F, inclusive
        """
        if not CGRAM_SLOT1 <= slot <= CGRAM_SLOT8:
            msg = f"Value {slot} out of range"
            raise ValueError(msg)
        if not isinstance(bytedata, list):
            msg = f"Expected list for bytedata, got {type(bytedata)}"
            raise TypeError(msg)
        if len(bytedata) != CHR_DATA_LENGTH:
            msg = "Bytes list must contain exactly 8 values"
            raise ValueError(msg)
        self.write(0x40 | (int(slot) << 3), mode=0)
        for byte in bytedata:
            self.write(byte, mode=1)

    def position_text(self, text: str, line: int, column: int = 1) -> None:
        """
        Display text at a given position on the LCD screen.

        Parameters
        ----------
        text: The string to display on the LCD
        line: The line to display the text
        column: The starting column for the text

        Note: both line and column are 1-based numbers, NOT 0-based
        """
        if not 1 <= line <= self.rows:
            msg = f"Line {line} out of range"
            raise ValueError(msg)
        if not 0 <= column <= self.width:
            msg = f"Column {column} out of range"
            raise ValueError(msg)
        self.write(LINES.get(line, LINES[1] | (column - 1)))
        for idx, ch in enumerate(text):
            self.write(ord(ch), mode=1)
            if column + idx > self.width:
                break

    def toggle_backlight(self) -> None:
        """
        Toggle the backlight.
        """
        self.backlight(not self.backlight_status)

    def clear(self) -> None:
        """
        Clear the LCD and turn off the backlight.
        """
        super().clear()
        self.backlight(False)

    def __str__(self) -> str:
        name = self.__class__.__name__
        addr = self.address
        rows = self.rows
        width = self.width
        stat = self.backlight_status
        return f"{name}(address={addr}, rows={rows}, width={width}, backlight_status={stat})"
