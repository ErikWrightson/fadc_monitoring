#!/bin/bash

set -euo pipefail

WATCH_DIR="/data/stage2"
PYTHON="/usr/bin/python3"
PYTHON_SCRIPT="/data/prad/checkFADC.py"

REPLAY_SCRIPT="~/prad2_daq/prad2evviewer/build/bin/prad2ana_replay_recon"

# Watch recursively for files that have finished being written
inotifywait -m -r -e close_write --format '%w%f' "$WATCH_DIR" |
while read -r FILE; do
    # Skip anything that isn't a regular file
    [[ -f "$FILE" ]] || continue

    SUBDIR=$(dirname "$FILE")

    # Count regular files directly inside this subdirectory
    FILE_COUNT=$(find "$SUBDIR" -maxdepth 1 -type f | wc -l)

    # If this is the first file in the directory, process it
    if [[ "$FILE_COUNT" -eq 1 ]]; then
        echo "First file in $SUBDIR: $FILE"
        "$REPLAY_SCRIPT" "-f $FILE -z 5 -o ./ -j 10 -x17"
        for rtFile in ./*.root ; do
            "$PYTHON" "$PYTHON_SCRIPT" "$rtFile" > $PDF_NAME
            RUN_NUM = ${PDF_NAME:5:6} 
            logentry -g Autolog -l TLOG -t "PRAD FADC run $RUN_NUM"  -a ./$PDF_NAME 
            rm $rtFile
            rm ./$PDF_NAME
        done
    fi
done