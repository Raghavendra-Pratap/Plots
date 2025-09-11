#!/bin/bash

# Simple Vault Update Script V2
# Quick way to update the clean vault using external configuration files

SOURCE_DIR="/Users/raghavendra_pratap/Developer"
SMART_SCRIPT="$SOURCE_DIR/smart-clean-vault-v2.sh"

echo "=== Updating Clean Vault V2 ==="
echo "Source: $SOURCE_DIR"
echo "Using external configuration files"
echo

if [ -f "$SMART_SCRIPT" ]; then
    echo "Running smart clean vault V2 script..."
    "$SMART_SCRIPT"
    echo
    echo "✅ Vault updated successfully!"
    echo "Location: /Users/raghavendra_pratap/Developer-Clean"
    echo
    echo "Configuration files:"
    echo "  - developer_ignore: Ignore patterns"
    echo "  - developer_bypass: Bypass patterns"
    echo
    echo "To modify ignore/bypass rules, edit these files and run this script again."
else
    echo "❌ ERROR: Smart script V2 not found at $SMART_SCRIPT"
    exit 1
fi
