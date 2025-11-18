#!/bin/bash
# Anki Debug Launcher
# This script launches Anki with console output visible for debugging

echo "Starting Anki with debug output..."
echo "Press Ctrl+C to stop Anki"
echo "----------------------------------------"

# Launch Anki using the launcher (updated for newer Anki versions)
if [ -f "/Applications/Anki.app/Contents/MacOS/launcher" ]; then
    /Applications/Anki.app/Contents/MacOS/launcher "$@" 2>&1
elif [ -f "/Applications/Anki.app/Contents/MacOS/anki" ]; then
    /Applications/Anki.app/Contents/MacOS/anki "$@" 2>&1
else
    echo "ERROR: Could not find Anki executable"
    echo "Checked:"
    echo "  - /Applications/Anki.app/Contents/MacOS/launcher"
    echo "  - /Applications/Anki.app/Contents/MacOS/anki"
    exit 1
fi

echo "----------------------------------------"
echo "Anki closed"
