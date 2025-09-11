# 🔄 Real-time Vault Watcher System

## 🎯 **What It Does**

The **Real-time File Watcher** automatically updates your Obsidian vault whenever files change in your development directory. No more manual updates needed!

## 🚀 **Quick Start**

### **Start the Watcher:**
```bash
./start-vault-watcher.sh
```

### **Check Status:**
```bash
./check-vault-watcher.sh
```

### **Stop the Watcher:**
```bash
./stop-vault-watcher.sh
```

## 📁 **System Files**

### **Core Scripts:**
- **`vault-watcher-v2.sh`** - Main file system watcher
- **`start-vault-watcher.sh`** - Start watcher in background
- **`stop-vault-watcher.sh`** - Stop watcher
- **`check-vault-watcher.sh`** - Check watcher status

### **Runtime Files:**
- **`vault-watcher.pid`** - Process ID file
- **`vault-watcher.log`** - Log file with all activity

## ⚙️ **How It Works**

### **1. File System Monitoring:**
- **Uses `fswatch`** to monitor your development directory
- **Watches recursively** for file changes
- **Excludes unwanted files** (logs, temp files, etc.)

### **2. Smart Filtering:**
- **Ignores directories**: `.git`, `node_modules`, `venv`, `__pycache__`
- **Ignores files**: `.DS_Store`, `.tmp`, `.log`, hidden files
- **Only triggers** on relevant file changes

### **3. Automatic Updates:**
- **Detects changes** in markdown files
- **Runs vault update** automatically
- **Logs all activity** for debugging

## 🔧 **Configuration**

### **What Triggers Updates:**
- **New markdown files** added to projects
- **Changes to existing** markdown files
- **New projects** with markdown files
- **Configuration changes** (ignore/bypass files)

### **What Doesn't Trigger Updates:**
- **Code files** (.py, .js, .ts, .rs, etc.)
- **Build artifacts** (node_modules, target/, dist/)
- **System files** (.DS_Store, .log, .tmp)
- **Hidden files** (starting with .)

## 📊 **Monitoring & Logs**

### **View Real-time Logs:**
```bash
tail -f vault-watcher.log
```

### **Check Recent Activity:**
```bash
tail -20 vault-watcher.log
```

### **View Full Log:**
```bash
cat vault-watcher.log
```

## 🎯 **Usage Examples**

### **Start Development Session:**
```bash
# Start the watcher
./start-vault-watcher.sh

# Check it's running
./check-vault-watcher.sh

# Start coding - vault updates automatically!
```

### **Stop Development Session:**
```bash
# Stop the watcher
./stop-vault-watcher.sh

# Check it's stopped
./check-vault-watcher.sh
```

### **Troubleshooting:**
```bash
# Check status
./check-vault-watcher.sh

# View logs
tail -f vault-watcher.log

# Restart if needed
./stop-vault-watcher.sh && ./start-vault-watcher.sh
```

## 🔄 **Update Frequency**

### **Real-time Updates:**
- **Immediate**: Updates as soon as files change
- **No delays**: No waiting for scheduled updates
- **Efficient**: Only updates when relevant files change

### **Performance:**
- **Low overhead**: Uses efficient file system events
- **Smart filtering**: Ignores irrelevant changes
- **Background process**: Doesn't interfere with your work

## 🚨 **Important Notes**

### **Prerequisites:**
- **`fswatch`** must be installed (installed via Homebrew)
- **macOS/Linux** only (Windows requires WSL)

### **Process Management:**
- **Background process**: Runs independently
- **PID tracking**: Prevents multiple instances
- **Graceful shutdown**: Properly stops when requested

### **Log Management:**
- **Log rotation**: Consider rotating logs for long-running sessions
- **Debug info**: Logs contain detailed information
- **Error tracking**: Failed updates are logged

## 🎉 **Benefits**

### **✅ Automatic Updates:**
- **No manual intervention** needed
- **Always up-to-date** vault
- **Seamless workflow** integration

### **✅ Smart Detection:**
- **Only relevant changes** trigger updates
- **Efficient monitoring** with minimal overhead
- **Intelligent filtering** of unwanted files

### **✅ Easy Management:**
- **Simple commands** to start/stop/check
- **Clear status** information
- **Comprehensive logging** for debugging

## 🔧 **Advanced Usage**

### **Custom Monitoring:**
Edit `vault-watcher-v2.sh` to modify:
- **Excluded patterns** (add more ignore rules)
- **Update triggers** (change what files trigger updates)
- **Logging level** (more or less verbose)

### **Integration with IDE:**
- **VS Code**: Works with any file changes
- **Terminal**: Works with command-line edits
- **Any editor**: Works with any file modifications

### **Background Service:**
- **Start on boot**: Add to startup scripts
- **System service**: Convert to systemd service (Linux)
- **LaunchAgent**: Create macOS LaunchAgent

## 📚 **Troubleshooting**

### **Common Issues:**

#### **Watcher not starting:**
```bash
# Check if fswatch is installed
which fswatch

# Install if missing
brew install fswatch
```

#### **Watcher not detecting changes:**
```bash
# Check if it's running
./check-vault-watcher.sh

# View logs for errors
tail -f vault-watcher.log
```

#### **Multiple instances:**
```bash
# Stop all instances
./stop-vault-watcher.sh

# Check for running processes
pgrep -f vault-watcher
```

### **Reset System:**
```bash
# Stop watcher
./stop-vault-watcher.sh

# Clean up files
rm -f vault-watcher.pid vault-watcher.log

# Restart
./start-vault-watcher.sh
```

---

## 🎯 **Summary**

The **Real-time Vault Watcher** provides:
- **Automatic updates** when files change
- **Smart filtering** of irrelevant changes
- **Easy management** with simple commands
- **Comprehensive logging** for debugging
- **Seamless integration** with your workflow

**Your vault now updates automatically!** 🎉

No more manual updates needed - just start the watcher and focus on your work!
