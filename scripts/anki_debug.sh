#!/bin/bash
# Anki Debug Launcher - VERBOSE (full output)
# Use anki_debug_dict.sh for filtered output instead

echo "🔍 Anki Debug Mode (VERBOSE - all output)"
echo "Press Ctrl+C to stop"
echo "=========================================="

# Set environment variable to signal auto-open
export ANKI_DICT_AUTO_OPEN=1

# Launch Anki with full output
if [ -f "/Applications/Anki.app/Contents/MacOS/launcher" ]; then
    /Applications/Anki.app/Contents/MacOS/launcher "$@" 2>&1
elif [ -f "/Applications/Anki.app/Contents/MacOS/anki" ]; then
    /Applications/Anki.app/Contents/MacOS/anki "$@" 2>&1
else
    echo "❌ ERROR: Could not find Anki executable"
    exit 1
fi

echo ""
echo "✓ Anki closed"
