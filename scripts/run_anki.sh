#!/bin/bash
# Launch Anki with console output for debugging
if [ -f "/Applications/Anki.app/Contents/MacOS/launcher" ]; then
    /Applications/Anki.app/Contents/MacOS/launcher "$@"
elif [ -f "/Applications/Anki.app/Contents/MacOS/anki" ]; then
    /Applications/Anki.app/Contents/MacOS/anki "$@"
else
    echo "ERROR: Could not find Anki executable"
    exit 1
fi
