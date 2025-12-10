#!/bin/bash
# Anki Debug Launcher - Quick test (auto-closes after 3s)

echo "🎨 Anki Debug Mode (QUICK TEST - auto-closes)"
echo "Mock opens for 3s then closes | Ctrl+C to stop early"
echo "=========================================="

# Set environment variables to open mock window with auto-close
export ANKI_DICT_AUTO_OPEN=1
export ANKI_DICT_OPEN_MOCK=1
export ANKI_DICT_AUTO_CLOSE=1

# Launch Anki and filter to show only errors/exceptions (not INFO logs)
if [ -f "/Applications/Anki.app/Contents/MacOS/launcher" ]; then
    /Applications/Anki.app/Contents/MacOS/launcher "$@" 2>&1 | grep -vE "INFO:" | grep -E "(Error|ERROR|Exception|Traceback|Warning|WARNING|Failed|FAILED|Critical|CRITICAL)" --line-buffered || true
elif [ -f "/Applications/Anki.app/Contents/MacOS/anki" ]; then
    /Applications/Anki.app/Contents/MacOS/anki "$@" 2>&1 | grep -vE "INFO:" | grep -E "(Error|ERROR|Exception|Traceback|Warning|WARNING|Failed|FAILED|Critical|CRITICAL)" --line-buffered || true
else
    echo "❌ ERROR: Could not find Anki executable"
    exit 1
fi

echo ""
echo "✓ Anki closed"