# Installation Guide

## Prerequisites

- Node.js (version 16 or higher)
- npm (comes with Node.js)
- Obsidian (version 0.15.0 or higher)

## Installation Methods

### Method 1: Manual Installation (Recommended)

1. **Download the Plugin**
   - Download the latest release from the [releases page](https://github.com/yourusername/obsidian-vault-ignore/releases)
   - Or clone this repository: `git clone https://github.com/yourusername/obsidian-vault-ignore.git`

2. **Build the Plugin**
   ```bash
   cd obsidian-vault-ignore
   ./build.sh
   ```

3. **Install to Obsidian**
   - Copy the entire plugin folder to your vault's `.obsidian/plugins/` directory
   - The folder should be named `vault-ignore`
   - Your vault structure should look like:
     ```
     your-vault/
     ├── .obsidian/
     │   └── plugins/
     │       └── vault-ignore/
     │           ├── main.js
     │           ├── manifest.json
     │           └── versions.json
     └── your-notes/
     ```

4. **Enable the Plugin**
   - Open Obsidian
   - Go to **Settings** → **Community plugins**
   - Make sure **Community plugins** is enabled
   - Find **Vault Ignore** in the list and toggle it on

### Method 2: Development Installation

1. **Clone and Setup**
   ```bash
   git clone https://github.com/yourusername/obsidian-vault-ignore.git
   cd obsidian-vault-ignore
   npm install
   ```

2. **Development Mode**
   ```bash
   npm run dev
   ```
   This will watch for changes and automatically rebuild the plugin.

3. **Copy to Vault**
   - Copy the built files (`main.js`, `manifest.json`, `versions.json`) to your vault's `.obsidian/plugins/vault-ignore/` directory

## Configuration

### Initial Setup

1. **Access Settings**
   - Go to **Settings** → **Community plugins** → **Vault Ignore** → **Settings**

2. **Configure Ignore Patterns**
   - **Ignore Patterns**: Add glob patterns for files and folders to ignore
   - **Ignore Extensions**: Specify file extensions to ignore
   - **Ignore Keywords**: Add keywords that, when found in filenames, will ignore those files
   - **Ignore Folders**: Specify folder names to ignore

3. **Enable Features**
   - **Enable File Explorer Filtering**: Hide ignored files from the file explorer
   - **Enable Search Exclusion**: Exclude ignored files from search results
   - **Enable .obsidianignore File**: Use a `.obsidianignore` file for project-specific ignores

### Using .obsidianignore File

1. **Create the File**
   - Create a `.obsidianignore` file in your vault root
   - Add ignore patterns following the same format as `.gitignore`

2. **Example .obsidianignore**
   ```
   # Development files
   **/node_modules/**
   **/.git/**
   **/dist/**
   **/build/**

   # System files
   **/.DS_Store
   **/Thumbs.db

   # Log files
   **/*.log
   **/*.tmp
   ```

## Commands

Access these commands through the Command Palette (`Ctrl/Cmd + P`):

- **Toggle Vault Ignore**: Enable/disable the ignore functionality
- **Refresh Ignore Patterns**: Manually refresh and reapply ignore patterns

## Troubleshooting

### Plugin Not Appearing

1. Check that the plugin files are in the correct location: `.obsidian/plugins/vault-ignore/`
2. Ensure the plugin is enabled in **Settings** → **Community plugins**
3. Restart Obsidian

### Files Still Showing

1. Check your ignore patterns in the plugin settings
2. Use the **Refresh Ignore Patterns** command
3. Verify that the patterns match the files you want to ignore

### Build Errors

1. Ensure Node.js and npm are installed
2. Run `npm install` to install dependencies
3. Check that all required files are present

## Uninstallation

1. **Disable the Plugin**
   - Go to **Settings** → **Community plugins**
   - Find **Vault Ignore** and toggle it off

2. **Remove Plugin Files**
   - Delete the `vault-ignore` folder from `.obsidian/plugins/`

3. **Restart Obsidian**
   - Close and reopen Obsidian to complete the uninstallation

## Support

If you encounter any issues:

1. Check the [troubleshooting section](#troubleshooting) above
2. Open an issue on the [GitHub repository](https://github.com/yourusername/obsidian-vault-ignore)
3. Check the [README.md](README.md) for more information
