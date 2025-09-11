#!/bin/bash

# Vault Watcher V2 - Real-time File System Watcher
# Monitors the development directory and automatically updates the clean vault

SOURCE_DIR="/Users/raghavendra_pratap/Developer"
CLEAN_VAULT_DIR="/Users/raghavendra_pratap/Developer-Clean"
UPDATE_SCRIPT="$SOURCE_DIR/update-vault-v2.sh"
LOG_FILE="$SOURCE_DIR/vault-watcher.log"

echo "=== Vault Watcher V2 - Real-time File System Watcher ==="
echo "Source: $SOURCE_DIR"
echo "Clean Vault: $CLEAN_VAULT_DIR"
echo "Update Script: $UPDATE_SCRIPT"
echo "Log File: $LOG_FILE"
echo

# Check if fswatch is installed
if ! command -v fswatch &> /dev/null; then
    echo "❌ ERROR: fswatch is not installed"
    echo "Please install it with: brew install fswatch"
    echo "Or visit: https://github.com/emcrisostomo/fswatch"
    exit 1
fi

# Check if update script exists
if [ ! -f "$UPDATE_SCRIPT" ]; then
    echo "❌ ERROR: Update script not found at $UPDATE_SCRIPT"
    exit 1
fi

# Create log file
touch "$LOG_FILE"

echo "✅ Starting file system watcher..."
echo "📁 Monitoring: $SOURCE_DIR"
echo "🔄 Auto-updating: $CLEAN_VAULT_DIR"
echo "📝 Logging to: $LOG_FILE"
echo
echo "Press Ctrl+C to stop the watcher"
echo

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to update vault
update_vault() {
    log_message "🔄 File change detected, updating vault..."
    
    # Run the update script
    if "$UPDATE_SCRIPT" >> "$LOG_FILE" 2>&1; then
        log_message "✅ Vault updated successfully"
        
        # Sync to GitHub
        log_message "🔄 Syncing to GitHub..."
        if "$SOURCE_DIR/git-sync-vault.sh" >> "$LOG_FILE" 2>&1; then
            log_message "✅ GitHub sync completed"
        else
            log_message "⚠️  GitHub sync failed - check git-sync log"
        fi
    else
        log_message "❌ Vault update failed - check log for details"
    fi
    
    log_message "⏳ Waiting for next change..."
    echo
}

# Initial vault update
log_message "🚀 Starting vault watcher..."
log_message "📁 Monitoring directory: $SOURCE_DIR"
log_message "🔄 Auto-updating vault: $CLEAN_VAULT_DIR"

# Run initial update
update_vault

# Start file system watcher
log_message "👀 File system watcher started - monitoring for changes..."

# Watch for changes in the source directory
# -r: recursive (watch subdirectories)
# -e: exclude patterns (ignore certain files/directories)
# -o: output format (just the path)
fswatch -r -e ".*" -e ".*/\.git/.*" -e ".*/node_modules/.*" -e ".*/venv/.*" -e ".*/__pycache__/.*" -e ".*/\.DS_Store" -e ".*/\.tmp" -e ".*/\.log" "$SOURCE_DIR" | while read -r changed_file; do
    # Skip if it's a directory
    if [ -d "$changed_file" ]; then
        continue
    fi
    
    # Skip if it's a hidden file (starts with .)
    if [[ "$(basename "$changed_file")" =~ ^\..* ]]; then
        continue
    fi
    
    # Skip if it's a log file
    if [[ "$changed_file" =~ \.(log|tmp|cache)$ ]]; then
        continue
    fi
    
    # Skip if it's in excluded directories
    if [[ "$changed_file" =~ /(\.git|node_modules|venv|__pycache__|\.DS_Store|\.tmp|\.log)/ ]]; then
        continue
    fi
    
    # Update vault for any other change
    update_vault
done
