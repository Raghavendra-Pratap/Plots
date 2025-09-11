#!/bin/bash

# Check Vault Watcher V2 Status
# Shows the current status of the file system watcher

SOURCE_DIR="/Users/raghavendra_pratap/Developer"
PID_FILE="$SOURCE_DIR/vault-watcher.pid"
LOG_FILE="$SOURCE_DIR/vault-watcher.log"

echo "=== Vault Watcher V2 Status Check ==="
echo "Source: $SOURCE_DIR"
echo "PID File: $PID_FILE"
echo "Log File: $LOG_FILE"
echo

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "❌ Vault watcher is NOT running"
    echo "📝 No PID file found"
    echo
    echo "To start: ./start-vault-watcher.sh"
    exit 1
fi

# Read PID from file
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Vault watcher is RUNNING"
    echo "📊 Process ID: $PID"
    echo "⏰ Started: $(ps -o lstart= -p "$PID")"
    echo "💾 Memory: $(ps -o rss= -p "$PID" | awk '{print $1/1024 " MB"}')"
    echo "🔄 Status: Monitoring for file changes"
    echo
    echo "📝 Recent log entries:"
    if [ -f "$LOG_FILE" ]; then
        tail -5 "$LOG_FILE" | sed 's/^/  /'
    else
        echo "  No log file found"
    fi
    echo
    echo "To stop: ./stop-vault-watcher.sh"
    echo "To view full logs: tail -f $LOG_FILE"
else
    echo "❌ Vault watcher is NOT running"
    echo "📝 Process with PID $PID not found"
    echo "🧹 Cleaning up stale PID file..."
    rm -f "$PID_FILE"
    echo
    echo "To start: ./start-vault-watcher.sh"
fi
