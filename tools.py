"""
Various utility functions.
"""

# SPDX-FileCopyrightText: © 2022 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

import sys
import socket
import traceback
from unicodedata import combining, normalize

import psutil


def eprint(*args, **kwargs):
    """
    Wrapper function for print() to use stderr instead of stdout.
    """
    print(*args, file=sys.stderr, **kwargs)


def str_to_bool(val, default=False) -> bool:
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


def gethostname() -> str:
    """
    Get the host name.
    """
    return socket.gethostname()


def net_addr() -> str:
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


def add_to_max(add1: int, add2: int, max_num: int) -> int:
    """
    Add two numbers, and wrap to max_num
    """
    return (add1 + add2) % max_num


def substr_wrap(string: str, start: int, length: int, wrap_pad: str = "") -> str:
    """
    Create a substring which starts at a given position, and extends
    for lenght characters, wrapping if the end of string is reached.

    Examples:
        print(substr_wrap("0123456789", 2, 15))
        => 0123456789
        # prints entire string

        print(substr_wrap("0123456789", 2, 5))
        => 23456
        # prints 5 characters starting at position 2

        print(substr_wrap("0123456789", 7, 5))
        => 78901
        # prints 5 characters starting at position 7, wrapping when needed

        print(substr_wrap("0123456789", 8, 5, " "))
        => 890 1
        # prints 5 characters starting at position 8, wrapping and padding as needed
    """
    if len(string) <= length:
        return string
    string = string + wrap_pad
    chrs = [string[add_to_max(start, i, len(string))] for i in range(length)]
    return "".join(chrs)


def dump_traceback(message: str = ""):
    """
    Print a traceback and optional message to stderr using eprint.
    """
    eprint(traceback.format_exc(), message, sep="\n")


LATIN = "ä æ  ǽ  đ ð ƒ ħ ı ł ø ǿ ö œ  ß  ŧ þ  ü Ä Æ  Ǽ  Đ Ð Ƒ Ħ I Ł Ø Ǿ Ö Œ  ẞ  Ŧ Þ  Ü"
ASCII = "a ae ae d d f h i l o o o oe ss t th u A AE AE D D F H I L O O O OE SS T TH U"
outliers = str.maketrans(dict(zip(LATIN.split(), ASCII.split())))


def remove_diacritics(s: str) -> str:
    """
    Remove diacritics from the provided string.
    """
    return "".join(c for c in normalize("NFD", s.translate(outliers)) if not combining(c))
