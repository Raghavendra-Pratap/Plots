import { App, Plugin, PluginSettingTab, Setting, TFile, TFolder, normalizePath } from 'obsidian';

interface VaultIgnoreSettings {
	ignorePatterns: string[];
	ignoreExtensions: string[];
	ignoreKeywords: string[];
	ignoreFolders: string[];
	enableFileExplorerFiltering: boolean;
	enableSearchExclusion: boolean;
	enableObsidianIgnoreFile: boolean;
	obsidianIgnoreFilePath: string;
}

const DEFAULT_SETTINGS: VaultIgnoreSettings = {
	ignorePatterns: [
		'**/node_modules/**',
		'**/.git/**',
		'**/dist/**',
		'**/build/**',
		'**/target/**',
		'**/venv/**',
		'**/__pycache__/**',
		'**/bounding-box-plotter-backup/**',
		'**/conflicting-apps-backup/**',
		'**/global-node-modules-backup/**',
		'**/electron-bundle/**',
		'**/tmp_playground/**',
		'**/.DS_Store',
		'**/Thumbs.db',
		'**/*.pyc',
		'**/*.pyo',
		'**/*.pyd',
		'**/*.rlib',
		'**/*.rmeta',
		'**/*.egg-info/**',
		'**/*.egg',
		'**/*.dmg',
		'**/*.exe',
		'**/*.AppImage',
		'**/*.deb',
		'**/*.rpm'
	],
	ignoreExtensions: [
		'.log',
		'.tmp',
		'.temp',
		'.cache',
		'.lock',
		'.pyc',
		'.pyo',
		'.pyd',
		'.so',
		'.rlib',
		'.rmeta',
		'.egg',
		'.dmg',
		'.exe',
		'.AppImage',
		'.deb',
		'.rpm',
		'.tgz',
		'.tar.gz',
		'.zip',
		'.rar',
		'.db',
		'.sqlite',
		'.sqlite3',
		'.pid',
		'.seed',
		'.bak',
		'.backup'
	],
	ignoreKeywords: [
		'backup',
		'temp',
		'temporary',
		'cache',
		'debug',
		'build',
		'dist',
		'target',
		'venv',
		'__pycache__',
		'node_modules',
		'coverage',
		'pytest',
		'tox',
		'hypothesis',
		'nosetests',
		'egg-info',
		'updates',
		'update'
	],
	ignoreFolders: [
		'node_modules',
		'.git',
		'dist',
		'build',
		'target',
		'venv',
		'env',
		'__pycache__',
		'.pytest_cache',
		'.coverage',
		'htmlcov',
		'.tox',
		'.cache',
		'.hypothesis',
		'bounding-box-plotter-backup',
		'conflicting-apps-backup',
		'global-node-modules-backup',
		'electron-bundle',
		'tmp_playground',
		'myScripts',
		'data_processing_output',
		'updates',
		'.obsidian'
	],
	enableFileExplorerFiltering: true,
	enableSearchExclusion: true,
	enableObsidianIgnoreFile: true,
	obsidianIgnoreFilePath: '.obsidianignore'
}

export default class VaultIgnorePlugin extends Plugin {
	settings: VaultIgnoreSettings;
	private originalFileExplorer: any;
	private originalSearch: any;
	private obsidianIgnorePatterns: string[] = [];
	private ignoreFileWatcher: any = null;

	async onload() {
		await this.loadSettings();

		// Load .obsidianignore patterns
		await this.loadObsidianIgnorePatterns();

		// Add settings tab
		this.addSettingTab(new VaultIgnoreSettingTab(this.app, this));

		// Initialize the ignore functionality
		this.initializeIgnoreFunctionality();

		// Add command to toggle ignore functionality
		this.addCommand({
			id: 'toggle-vault-ignore',
			name: 'Toggle Vault Ignore',
			callback: () => {
				this.toggleIgnoreFunctionality();
			}
		});

		// Add command to refresh ignore patterns
		this.addCommand({
			id: 'refresh-ignore-patterns',
			name: 'Refresh Ignore Patterns',
			callback: () => {
				this.refreshIgnorePatterns();
			}
		});

		// Set up file watcher for .obsidianignore file
		this.setupIgnoreFileWatcher();
	}

	onunload() {
		// Clean up file watcher
		if (this.ignoreFileWatcher) {
			this.app.vault.offref(this.ignoreFileWatcher);
		}
		
		// Restore original functionality
		this.restoreOriginalFunctionality();
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}

	async loadObsidianIgnorePatterns() {
		if (!this.settings.enableObsidianIgnoreFile) {
			this.obsidianIgnorePatterns = [];
			return;
		}

		try {
			const ignoreFile = this.app.vault.getAbstractFileByPath(this.settings.obsidianIgnoreFilePath);
			if (ignoreFile && ignoreFile instanceof TFile) {
				const content = await this.app.vault.read(ignoreFile);
				this.obsidianIgnorePatterns = content.split('\n')
					.map(line => line.trim())
					.filter(line => line && !line.startsWith('#')); // Remove comments and empty lines
			} else {
				this.obsidianIgnorePatterns = [];
			}
		} catch (error) {
			console.error('Error loading .obsidianignore patterns:', error);
			this.obsidianIgnorePatterns = [];
		}
	}

	initializeIgnoreFunctionality() {
		if (this.settings.enableFileExplorerFiltering) {
			this.patchFileExplorer();
		}
		
		if (this.settings.enableSearchExclusion) {
			this.patchSearch();
		}
	}

	patchFileExplorer() {
		// Store original file explorer methods
		const fileExplorer = this.app.workspace.getLeavesOfType('file-explorer')[0]?.view as any;
		if (fileExplorer) {
			this.originalFileExplorer = {
				createFileTree: fileExplorer.createFileTree,
				shouldShowFile: fileExplorer.shouldShowFile
			};

			// Patch the file explorer to filter out ignored files
			if (fileExplorer.createFileTree) {
				const originalCreateFileTree = fileExplorer.createFileTree.bind(fileExplorer);
				fileExplorer.createFileTree = (folder: TFolder) => {
					const tree = originalCreateFileTree(folder);
					return this.filterFileTree(tree);
				};
			}

			// Patch shouldShowFile method if it exists
			if (fileExplorer.shouldShowFile) {
				const originalShouldShowFile = fileExplorer.shouldShowFile.bind(fileExplorer);
				fileExplorer.shouldShowFile = (file: TFile) => {
					if (this.isFileIgnored(file)) {
						return false;
					}
					return originalShouldShowFile(file);
				};
			}
		}
	}

	patchSearch() {
		// Store original search functionality
		const searchPlugin = (this.app as any).plugins.plugins['global-search'];
		if (searchPlugin) {
			this.originalSearch = {
				search: searchPlugin.search
			};

			// Patch search to exclude ignored files
			const originalSearch = searchPlugin.search.bind(searchPlugin);
			searchPlugin.search = (query: string, options: any) => {
				// Filter out ignored files from search results
				const results = originalSearch(query, options);
				if (results && results.results) {
					results.results = results.results.filter((result: any) => {
						if (result.file && this.isFileIgnored(result.file)) {
							return false;
						}
						return true;
					});
				}
				return results;
			};
		}
	}

	filterFileTree(tree: any): any {
		if (!tree) return tree;

		// Filter children if they exist
		if (tree.children) {
			tree.children = tree.children.filter((child: any) => {
				if (child.file && this.isFileIgnored(child.file)) {
					return false;
				}
				if (child.folder && this.isFolderIgnored(child.folder)) {
					return false;
				}
				// Recursively filter children
				if (child.children) {
					child.children = this.filterFileTree(child).children;
				}
				return true;
			});
		}

		return tree;
	}

	isFileIgnored(file: TFile): boolean {
		const path = normalizePath(file.path);
		
		// Check against ignore patterns
		for (const pattern of this.settings.ignorePatterns) {
			if (this.matchesPattern(path, pattern)) {
				return true;
			}
		}

		// Check against extensions
		for (const ext of this.settings.ignoreExtensions) {
			if (file.extension === ext.substring(1)) { // Remove the dot
				return true;
			}
		}

		// Check against keywords in filename
		for (const keyword of this.settings.ignoreKeywords) {
			if (file.name.toLowerCase().includes(keyword.toLowerCase())) {
				return true;
			}
		}

		// Check .obsidianignore file if enabled
		if (this.settings.enableObsidianIgnoreFile) {
			return this.checkObsidianIgnoreFile(file);
		}

		return false;
	}

	isFolderIgnored(folder: TFolder): boolean {
		const path = normalizePath(folder.path);
		
		// Check against ignore patterns
		for (const pattern of this.settings.ignorePatterns) {
			if (this.matchesPattern(path, pattern)) {
				return true;
			}
		}

		// Check against ignore folders
		for (const ignoreFolder of this.settings.ignoreFolders) {
			if (folder.name === ignoreFolder || path.includes(ignoreFolder)) {
				return true;
			}
		}

		// Check against keywords in folder name
		for (const keyword of this.settings.ignoreKeywords) {
			if (folder.name.toLowerCase().includes(keyword.toLowerCase())) {
				return true;
			}
		}

		return false;
	}

	matchesPattern(path: string, pattern: string): boolean {
		// Convert glob pattern to regex
		const regexPattern = pattern
			.replace(/\*\*/g, '.*')  // ** matches any number of directories
			.replace(/\*/g, '[^/]*') // * matches any characters except /
			.replace(/\?/g, '[^/]')  // ? matches any single character except /
			.replace(/\./g, '\\.');  // Escape dots

		const regex = new RegExp('^' + regexPattern + '$');
		return regex.test(path);
	}

	checkObsidianIgnoreFile(file: TFile): boolean {
		// Check against loaded .obsidianignore patterns
		for (const pattern of this.obsidianIgnorePatterns) {
			if (this.matchesPattern(file.path, pattern)) {
				return true;
			}
		}
		return false;
	}

	toggleIgnoreFunctionality() {
		this.settings.enableFileExplorerFiltering = !this.settings.enableFileExplorerFiltering;
		this.settings.enableSearchExclusion = !this.settings.enableSearchExclusion;
		this.saveSettings();
		this.refreshIgnorePatterns();
	}

	async refreshIgnorePatterns() {
		// Reload .obsidianignore patterns
		await this.loadObsidianIgnorePatterns();
		
		// Re-initialize the ignore functionality
		this.restoreOriginalFunctionality();
		this.initializeIgnoreFunctionality();
		
		// Refresh the file explorer
		const fileExplorer = this.app.workspace.getLeavesOfType('file-explorer')[0]?.view as any;
		if (fileExplorer && fileExplorer.requestSort) {
			fileExplorer.requestSort();
		}
	}

	restoreOriginalFunctionality() {
		// Restore original file explorer methods
		const fileExplorer = this.app.workspace.getLeavesOfType('file-explorer')[0]?.view as any;
		if (fileExplorer && this.originalFileExplorer) {
			if (this.originalFileExplorer.createFileTree) {
				fileExplorer.createFileTree = this.originalFileExplorer.createFileTree;
			}
			if (this.originalFileExplorer.shouldShowFile) {
				fileExplorer.shouldShowFile = this.originalFileExplorer.shouldShowFile;
			}
		}

		// Restore original search methods
		const searchPlugin = (this.app as any).plugins.plugins['global-search'];
		if (searchPlugin && this.originalSearch) {
			searchPlugin.search = this.originalSearch.search;
		}
	}

	setupIgnoreFileWatcher() {
		if (!this.settings.enableObsidianIgnoreFile) {
			return;
		}

		// Watch for changes to the .obsidianignore file
		this.ignoreFileWatcher = this.app.vault.on('modify', (file) => {
			if (file.path === this.settings.obsidianIgnoreFilePath) {
				this.loadObsidianIgnorePatterns();
			}
		});
	}
}

class VaultIgnoreSettingTab extends PluginSettingTab {
	plugin: VaultIgnorePlugin;

	constructor(app: App, plugin: VaultIgnorePlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;
		containerEl.empty();

		containerEl.createEl('h2', { text: 'Vault Ignore Settings' });

		// Ignore Patterns
		new Setting(containerEl)
			.setName('Ignore Patterns')
			.setDesc('Glob patterns for files and folders to ignore (one per line)')
			.addTextArea(text => text
				.setPlaceholder('**/node_modules/**\n**/.git/**\n**/dist/**')
				.setValue(this.plugin.settings.ignorePatterns.join('\n'))
				.onChange(async (value) => {
					this.plugin.settings.ignorePatterns = value.split('\n').filter(p => p.trim());
					await this.plugin.saveSettings();
				}));

		// Ignore Extensions
		new Setting(containerEl)
			.setName('Ignore Extensions')
			.setDesc('File extensions to ignore (one per line, with or without dot)')
			.addTextArea(text => text
				.setPlaceholder('.log\n.tmp\n.cache')
				.setValue(this.plugin.settings.ignoreExtensions.join('\n'))
				.onChange(async (value) => {
					this.plugin.settings.ignoreExtensions = value.split('\n').filter(e => e.trim());
					await this.plugin.saveSettings();
				}));

		// Ignore Keywords
		new Setting(containerEl)
			.setName('Ignore Keywords')
			.setDesc('Keywords in filenames to ignore (one per line)')
			.addTextArea(text => text
				.setPlaceholder('backup\ntemp\ncache')
				.setValue(this.plugin.settings.ignoreKeywords.join('\n'))
				.onChange(async (value) => {
					this.plugin.settings.ignoreKeywords = value.split('\n').filter(k => k.trim());
					await this.plugin.saveSettings();
				}));

		// Ignore Folders
		new Setting(containerEl)
			.setName('Ignore Folders')
			.setDesc('Folder names to ignore (one per line)')
			.addTextArea(text => text
				.setPlaceholder('node_modules\n.git\ndist')
				.setValue(this.plugin.settings.ignoreFolders.join('\n'))
				.onChange(async (value) => {
					this.plugin.settings.ignoreFolders = value.split('\n').filter(f => f.trim());
					await this.plugin.saveSettings();
				}));

		// Enable File Explorer Filtering
		new Setting(containerEl)
			.setName('Enable File Explorer Filtering')
			.setDesc('Hide ignored files and folders from the file explorer')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.enableFileExplorerFiltering)
				.onChange(async (value) => {
					this.plugin.settings.enableFileExplorerFiltering = value;
					await this.plugin.saveSettings();
					this.plugin.refreshIgnorePatterns();
				}));

		// Enable Search Exclusion
		new Setting(containerEl)
			.setName('Enable Search Exclusion')
			.setDesc('Exclude ignored files from search results')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.enableSearchExclusion)
				.onChange(async (value) => {
					this.plugin.settings.enableSearchExclusion = value;
					await this.plugin.saveSettings();
					this.plugin.refreshIgnorePatterns();
				}));

		// Enable .obsidianignore File
		new Setting(containerEl)
			.setName('Enable .obsidianignore File')
			.setDesc('Read ignore patterns from a .obsidianignore file in your vault root')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.enableObsidianIgnoreFile)
				.onChange(async (value) => {
					this.plugin.settings.enableObsidianIgnoreFile = value;
					await this.plugin.saveSettings();
				}));

		// .obsidianignore File Path
		new Setting(containerEl)
			.setName('.obsidianignore File Path')
			.setDesc('Path to the ignore file (relative to vault root)')
			.addText(text => text
				.setPlaceholder('.obsidianignore')
				.setValue(this.plugin.settings.obsidianIgnoreFilePath)
				.onChange(async (value) => {
					this.plugin.settings.obsidianIgnoreFilePath = value;
					await this.plugin.saveSettings();
				}));

		// Refresh Button
		new Setting(containerEl)
			.setName('Refresh Ignore Patterns')
			.setDesc('Manually refresh the ignore patterns and reapply filtering')
			.addButton(button => button
				.setButtonText('Refresh')
				.onClick(() => {
					this.plugin.refreshIgnorePatterns();
				}));
	}
}
