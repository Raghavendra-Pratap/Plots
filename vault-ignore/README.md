# Vault Ignore Plugin

A powerful Obsidian plugin that provides `.gitignore`-like functionality for your vault, allowing you to exclude files, folders, extensions, and keywords from indexing and search.

## Features

- **File Pattern Matching**: Use glob patterns to ignore specific files and folders
- **Extension Filtering**: Exclude files by their extensions
- **Keyword Filtering**: Ignore files containing specific keywords in their names
- **Folder Exclusion**: Hide entire folders from the file explorer
- **File Explorer Integration**: Automatically hide ignored files from the file explorer
- **Search Exclusion**: Exclude ignored files from search results
- **`.obsidianignore` Support**: Use a `.obsidianignore` file for project-specific ignores
- **Real-time Updates**: Changes to ignore patterns are applied immediately

## Installation

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/yourusername/obsidian-vault-ignore/releases)
2. Extract the plugin files to your vault's `.obsidian/plugins/vault-ignore/` folder
3. Enable the plugin in Obsidian's Community Plugins settings

### Development Installation

1. Clone this repository
2. Run `npm install` to install dependencies
3. Run `npm run build` to build the plugin
4. Copy the built files to your vault's `.obsidian/plugins/vault-ignore/` folder

## Usage

### Settings

Access the plugin settings through **Settings → Community plugins → Vault Ignore**.

#### Ignore Patterns
Use glob patterns to match files and folders:
- `**/node_modules/**` - Ignore all node_modules folders
- `**/.git/**` - Ignore .git folders
- `**/*.log` - Ignore all .log files
- `**/dist/**` - Ignore dist folders

#### Ignore Extensions
Specify file extensions to ignore (with or without the dot):
- `.log`
- `.tmp`
- `.cache`
- `.lock`

#### Ignore Keywords
Ignore files containing specific keywords in their names:
- `backup`
- `temp`
- `temporary`
- `cache`

#### Ignore Folders
Specify folder names to ignore:
- `node_modules`
- `.git`
- `dist`
- `build`

### Commands

The plugin provides several commands accessible through the Command Palette:

- **Toggle Vault Ignore**: Enable/disable the ignore functionality
- **Refresh Ignore Patterns**: Manually refresh and reapply ignore patterns

### .obsidianignore File

Create a `.obsidianignore` file in your vault root to define project-specific ignore patterns. This file follows the same format as `.gitignore`:

```
# Ignore node modules
**/node_modules/**

# Ignore build artifacts
**/dist/**
**/build/**

# Ignore log files
**/*.log

# Ignore temporary files
**/*.tmp
**/*.temp
```

## Default Ignore Patterns

The plugin comes with sensible defaults that ignore common development files:

- `**/node_modules/**`
- `**/.git/**`
- `**/dist/**`
- `**/build/**`
- `**/.DS_Store`
- `**/Thumbs.db`

And common file extensions:
- `.log`
- `.tmp`
- `.temp`
- `.cache`
- `.lock`

## Development

### Building

```bash
npm run build
```

### Development Mode

```bash
npm run dev
```

This will watch for changes and automatically rebuild the plugin.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

If you encounter any issues or have feature requests, please open an issue on the [GitHub repository](https://github.com/yourusername/obsidian-vault-ignore).
