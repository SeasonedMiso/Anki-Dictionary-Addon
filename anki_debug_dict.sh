#!/bin/bash
# Anki Debug Launcher - Opens UI MOCK window (errors only)

echo "🎨 Anki Debug Mode (UI MOCK - errors only)"
echo "Mock window auto-opens | Ctrl+C to stop"
echo "=========================================="

# Set environment variables to open mock window
export ANKI_DICT_AUTO_OPEN=1
export ANKI_DICT_OPEN_MOCK=1

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
