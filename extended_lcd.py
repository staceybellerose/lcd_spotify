"""
Extended LCD class with convenience functions.
"""

# SPDX-FileCopyrightText: © 2022 Stacey Adams <stacey.belle.rose [AT] gmail [DOT] com>
# SPDX-License-Identifier: MIT

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

class ExtendedLcd(LCD):
    """
    Extended LCD class with convenience functions.
    """
    def save_cgram_char(self, slot, bytedata):
        """
        Load bytedata into LCD's CGRAM
        """
        if slot < 0 or slot > 7:
            raise ValueError(f"Value {slot} out of range")
        if not isinstance(bytedata, list):
            raise TypeError(f"Expected list for bytedata, got {type(bytedata)}")
        if len(bytedata) != 8:
            raise ValueError("Bytes list must contain exactly 8 values")
        self.write(0x40 | (int(slot) << 3), mode=0)
        for byte in bytedata:
            self.write(byte, mode=1)

    def position_text(self, text, line, column=1):
        """
        Display text at a given position on the LCD screen.

        text: the string to display
        line: the line to display the text
        column: the starting column for the text

        Note: both line and column are 1-based numbers, NOT 0-based
        """
        if line < 1 or line > self.rows:
            raise ValueError(f"Line {line} out of range")
        if column < 1 or column > self.width:
            raise ValueError("Column {column} out of range")
        self.write(LINES.get(line, LINES[1] | (column - 1)))
        for idx, ch in text:
            self.write(ord(ch), mode=1)
            if column + idx > self.width:
                break
