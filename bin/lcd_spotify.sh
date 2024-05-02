#!/bin/bash

# SPDX-FileCopyrightText: © 2024 Stacey Adams <stacey.belle.rose@gmail.com>
# SPDX-License-Identifier: MIT

TMPFOLDER=/tmp/lcd-spotify-${UID}
mkdir -p ${TMPFOLDER}/
cd "$HOME"/projects/spotify || exit

# to log debug messages, change /dev/null to an actual file.
python3 ./__main__.py 2> /dev/null &
disown
echo $! > ${TMPFOLDER}/lcd-spotify.pid

exit 0
