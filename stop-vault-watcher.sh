#!/bin/bash

# Stop Vault Watcher V2 - Background Service
# Stops the file system watcher

SOURCE_DIR="/Users/raghavendra_pratap/Developer"
PID_FILE="$SOURCE_DIR/vault-watcher.pid"
LOG_FILE="$SOURCE_DIR/vault-watcher.log"

echo "=== Stopping Vault Watcher V2 Background Service ==="
echo "Source: $SOURCE_DIR"
echo "PID File: $PID_FILE"
echo "Log File: $LOG_FILE"
echo

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  No PID file found - watcher may not be running"
    echo "Checking for running processes..."
    
    # Check if any vault watcher processes are running
    if pgrep -f "vault-watcher-v2.sh" > /dev/null; then
        echo "🔍 Found running vault watcher processes:"
        pgrep -f "vault-watcher-v2.sh"
        echo "Killing them..."
        pkill -f "vault-watcher-v2.sh"
        echo "✅ Killed running processes"
    else
        echo "✅ No vault watcher processes found"
    fi
    exit 0
fi

# Read PID from file
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "🛑 Stopping vault watcher (PID: $PID)..."
    
    # Try graceful shutdown first
    kill "$PID"
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Check if still running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Graceful shutdown failed, forcing stop..."
        kill -9 "$PID"
        sleep 1
    fi
    
    # Final check
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ Failed to stop vault watcher"
        exit 1
    else
        echo "✅ Vault watcher stopped successfully"
    fi
else
    echo "⚠️  Process with PID $PID is not running"
    echo "Cleaning up stale PID file..."
fi

# Clean up PID file
rm -f "$PID_FILE"
echo "🧹 Cleaned up PID file"

echo
echo "✅ Vault watcher stopped successfully!"
echo "📝 Log file preserved: $LOG_FILE"
echo "🔄 Auto-updating is now disabled"
echo
echo "To start again: ./start-vault-watcher.sh"
