#!/bin/bash

# Git Sync Vault - Auto-commit and push vault changes
# This script is called by the file watcher when vault is updated

VAULT_DIR="/Users/raghavendra_pratap/Developer-Clean"
LOG_FILE="/Users/raghavendra_pratap/Developer/vault-git-sync.log"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "🔄 Starting Git sync for vault..."

# Change to vault directory
cd "$VAULT_DIR" || {
    log_message "❌ Failed to change to vault directory: $VAULT_DIR"
    exit 1
}

# Check if there are any changes
if git diff --quiet && git diff --cached --quiet; then
    log_message "ℹ️  No changes to commit"
    exit 0
fi

# Add all changes
log_message "📝 Adding changes to Git..."
git add .

# Create commit with timestamp
COMMIT_MSG="Auto-sync: Vault updated $(date '+%Y-%m-%d %H:%M:%S')"
log_message "💾 Committing changes: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Push to GitHub
log_message "🚀 Pushing to GitHub..."
if git push origin master; then
    log_message "✅ Successfully synced to GitHub"
else
    log_message "❌ Failed to push to GitHub"
    exit 1
fi

log_message "🎉 Git sync completed successfully!"


