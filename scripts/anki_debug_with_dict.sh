#!/bin/bash
# Anki Debug Launcher with Auto-Open Dictionary
# This script launches Anki with:
# 1. Console output visible for debugging
# 2. Dictionary window automatically opened on startup

echo "=========================================="
echo "Anki Debug Mode with Dictionary Auto-Open"
echo "=========================================="
echo ""

# Get Anki addon directory
ADDON_DIR="$HOME/Library/Application Support/Anki2/addons21"

# Find the addon folder (looks for manifest.json with our addon name)
ADDON_FOLDER=""
for dir in "$ADDON_DIR"/*; do
    if [ -f "$dir/manifest.json" ]; then
        if grep -q "Anki Dictionary" "$dir/manifest.json" 2>/dev/null; then
            ADDON_FOLDER="$dir"
            break
        fi
    fi
done

if [ -z "$ADDON_FOLDER" ]; then
    echo "⚠️  Warning: Could not find Anki Dictionary addon folder"
    echo "Dictionary auto-open may not work"
    echo ""
else
    CONFIG_FILE="$ADDON_FOLDER/meta.json"
    
    # Backup existing config
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
        echo "✓ Backed up config to meta.json.backup"
    fi
    
    # Enable dictOnStart in config
    if [ -f "$CONFIG_FILE" ]; then
        # Use Python to safely update JSON
        python3 << EOF
import json
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    
    config['dictOnStart'] = True
    
    with open('$CONFIG_FILE', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("✓ Enabled dictionary auto-open (dictOnStart=true)")
except Exception as e:
    print(f"⚠️  Could not update config: {e}")
EOF
    else
        echo "⚠️  Config file not found at: $CONFIG_FILE"
    fi
    
    echo ""
fi

echo "Starting Anki with debug output..."
echo "Dictionary will open automatically on profile load"
echo "Press Ctrl+C to stop Anki"
echo "=========================================="
echo ""

# Launch Anki using the launcher
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

echo ""
echo "=========================================="
echo "Anki closed"

# Restore original config
if [ -n "$ADDON_FOLDER" ] && [ -f "$CONFIG_FILE.backup" ]; then
    mv "$CONFIG_FILE.backup" "$CONFIG_FILE"
    echo "✓ Restored original config"
fi

echo "=========================================="
