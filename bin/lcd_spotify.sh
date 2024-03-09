#!/bin/bash

# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

mkdir -p /tmp/lcd-spotify/
cd "$HOME"/projects/spotify || exit
python3 ./lcd_spotify.py &
disown
echo $! > /tmp/lcd-spotify/lcd-spotify.pid

exit 0
