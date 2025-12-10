#!/bin/bash
# Anki Debug Launcher - Quick test with proper cleanup

echo "🎨 Anki Debug Mode (QUICK TEST)"
echo "=========================================="

# Kill any existing Anki processes
echo "Killing existing Anki processes..."
pkill -9 -f "Anki" 2>/dev/null || true
pkill -9 -f "anki" 2>/dev/null || true
sleep 3

# Set environment variables to open mock window with auto-close
export ANKI_DICT_AUTO_OPEN=1
export ANKI_DICT_OPEN_MOCK=1
export ANKI_DICT_AUTO_CLOSE=1

# Launch Anki and capture all output
echo "Starting Anki..."
ANKI_OUTPUT=$(mktemp)

if [ -f "/Applications/Anki.app/Contents/MacOS/launcher" ]; then
    /Applications/Anki.app/Contents/MacOS/launcher "$@" > "$ANKI_OUTPUT" 2>&1 &
    ANKI_PID=$!
elif [ -f "/Applications/Anki.app/Contents/MacOS/anki" ]; then
    /Applications/Anki.app/Contents/MacOS/anki "$@" > "$ANKI_OUTPUT" 2>&1 &
    ANKI_PID=$!
else
    echo "❌ ERROR: Could not find Anki executable"
    exit 1
fi

# Wait for Anki to finish (with timeout)
timeout 10 wait $ANKI_PID 2>/dev/null || true

# Give it a moment to clean up
sleep 2

# Kill any remaining Anki processes
pkill -9 -f "Anki.app" 2>/dev/null || true
pkill -9 -f "anki" 2>/dev/null || true

# Wait for processes to die
sleep 2

# Show errors and warnings
echo ""
echo "========== ERRORS & WARNINGS =========="
if grep -E "(Error|ERROR|Exception|Traceback|Warning|WARNING|Failed|FAILED|Critical|CRITICAL)" "$ANKI_OUTPUT" > /dev/null; then
    grep -E "(Error|ERROR|Exception|Traceback|Warning|WARNING|Failed|FAILED|Critical|CRITICAL)" "$ANKI_OUTPUT"
else
    echo "✓ No errors detected"
fi

# Show full output if there were errors
if grep -E "Traceback|Exception" "$ANKI_OUTPUT" > /dev/null; then
    echo ""
    echo "========== FULL OUTPUT =========="
    cat "$ANKI_OUTPUT"
fi

rm -f "$ANKI_OUTPUT"
echo ""
echo "✓ Done"