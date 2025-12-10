#!/bin/bash
# Anki Debug Launcher - Opens UI MOCK window (errors only) on separate virtual desktop

echo "🎨 Anki Debug Mode (UI MOCK - errors only)"
echo "Mock window stays open | Ctrl+C to stop"
echo "Opening on separate virtual desktop..."
echo "=========================================="

# Set environment variables to open mock window (no auto-close)
export ANKI_DICT_AUTO_OPEN=1
export ANKI_DICT_OPEN_MOCK=1

# Function to move Anki to a different desktop using AppleScript
move_to_desktop() {
    sleep 2  # Wait for Anki to launch
    osascript <<EOF
tell application "System Events"
    tell application "Anki" to activate
    delay 1
    
    -- Create new desktop if needed and move Anki there
    tell application "Mission Control" to activate
    delay 1
    
    -- Move to new desktop (Desktop 2 or create one)
    key code 124 using {control down}  -- Ctrl+Right Arrow to next desktop
    delay 0.5
    
    tell application "Anki" to activate
end tell
EOF
}

# Launch Anki in background and move to different desktop
if [ -f "/Applications/Anki.app/Contents/MacOS/launcher" ]; then
    # Start Anki in background
    /Applications/Anki.app/Contents/MacOS/launcher "$@" 2>&1 | grep -vE "INFO:" | grep -E "(Error|ERROR|Exception|Traceback|Warning|WARNING|Failed|FAILED|Critical|CRITICAL)" --line-buffered &
    ANKI_PID=$!
    
    # Move to different desktop
    move_to_desktop &
    
    # Wait for Anki process
    wait $ANKI_PID
elif [ -f "/Applications/Anki.app/Contents/MacOS/anki" ]; then
    # Start Anki in background
    /Applications/Anki.app/Contents/MacOS/anki "$@" 2>&1 | grep -vE "INFO:" | grep -E "(Error|ERROR|Exception|Traceback|Warning|WARNING|Failed|FAILED|Critical|CRITICAL)" --line-buffered &
    ANKI_PID=$!
    
    # Move to different desktop
    move_to_desktop &
    
    # Wait for Anki process
    wait $ANKI_PID
else
    echo "❌ ERROR: Could not find Anki executable"
    exit 1
fi

echo ""
echo "✓ Anki closed"
