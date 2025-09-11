#!/bin/bash

# Start Vault Watcher V2 - Background Service
# Starts the file system watcher in the background

SOURCE_DIR="/Users/raghavendra_pratap/Developer"
WATCHER_SCRIPT="$SOURCE_DIR/vault-watcher-v2.sh"
PID_FILE="$SOURCE_DIR/vault-watcher.pid"
LOG_FILE="$SOURCE_DIR/vault-watcher.log"

echo "=== Starting Vault Watcher V2 Background Service ==="
echo "Source: $SOURCE_DIR"
echo "Watcher: $WATCHER_SCRIPT"
echo "PID File: $PID_FILE"
echo "Log File: $LOG_FILE"
echo

# Check if watcher is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Vault watcher is already running (PID: $PID)"
        echo "To stop it, run: ./stop-vault-watcher.sh"
        echo "To restart it, run: ./stop-vault-watcher.sh && ./start-vault-watcher.sh"
        exit 1
    else
        echo "🧹 Cleaning up stale PID file..."
        rm -f "$PID_FILE"
    fi
fi

# Check if fswatch is installed
if ! command -v fswatch &> /dev/null; then
    echo "❌ ERROR: fswatch is not installed"
    echo "Please install it with: brew install fswatch"
    echo "Or visit: https://github.com/emcrisostomo/fswatch"
    exit 1
fi

# Start the watcher in background
echo "🚀 Starting vault watcher in background..."
nohup "$WATCHER_SCRIPT" > "$LOG_FILE" 2>&1 &
WATCHER_PID=$!

# Save PID to file
echo "$WATCHER_PID" > "$PID_FILE"

echo "✅ Vault watcher started successfully!"
echo "📊 Process ID: $WATCHER_PID"
echo "📝 Log file: $LOG_FILE"
echo "🔄 Auto-updating vault on file changes"
echo
echo "To stop the watcher: ./stop-vault-watcher.sh"
echo "To view logs: tail -f $LOG_FILE"
echo "To check status: ./check-vault-watcher.sh"
