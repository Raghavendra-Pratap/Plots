# 🔄 Auto-Updater System & Release Workflow

## Overview

Data Studio v2 includes a comprehensive auto-updater system that automatically checks for new versions and handles updates seamlessly. The system integrates with GitHub releases and provides both automatic and manual update options.

## 🚀 Features

### Auto-Update System
- **Automatic Version Checking**: Checks for updates every hour (configurable)
- **GitHub Integration**: Monitors releases from the GitHub repository
- **Smart Version Comparison**: Compares semantic versions to determine updates
- **User Notifications**: System notifications and in-app alerts for available updates
- **Background Downloads**: Downloads updates when the app is idle
- **Automatic Installation**: Installs updates on app restart

### Release Workflow
- **Automated Builds**: GitHub Actions workflow for cross-platform builds
- **Version Management**: Automatic version bumping and tagging
- **Asset Distribution**: Uploads platform-specific installers to GitHub releases
- **Release Notes**: Automated changelog generation and release documentation

## 🏗️ Architecture

### Frontend (React/TypeScript)
```
frontend/src/services/AutoUpdater.ts
├── UpdateInfo interface
├── UpdateProgress interface
├── AutoUpdaterService class
│   ├── startAutoUpdateCheck()
│   ├── checkForUpdates()
│   ├── downloadUpdate()
│   ├── installUpdate()
│   └── Event handlers
```

### Main Process (Electron)
```
frontend/public/updateHandler.js
├── UpdateHandler class
├── IPC handlers
├── Auto-updater configuration
├── Download management
└── Installation handling
```

### GitHub Actions
```
.github/workflows/release.yml
├── Multi-platform builds
├── Automated releases
├── Asset uploads
└── Version management
```

## 📋 How It Works

### 1. Update Detection
```typescript
// The service automatically checks GitHub releases
const response = await fetch('https://api.github.com/repos/Raghavendra-Pratap/Data_Studio/releases/latest');
const release = await response.json();
const latestVersion = release.tag_name.replace('v', '');

if (this.isNewerVersion(latestVersion, currentVersion)) {
  // Notify user and offer update
}
```

### 2. Version Comparison
```typescript
private isNewerVersion(newVersion: string, currentVersion: string): boolean {
  const newParts = newVersion.split('.').map(Number);
  const currentParts = currentVersion.split('.').map(Number);
  
  for (let i = 0; i < Math.max(newParts.length, currentParts.length); i++) {
    const newPart = newParts[i] || 0;
    const currentPart = currentParts[i] || 0;
    
    if (newPart > currentPart) return true;
    if (newPart < currentPart) return false;
  }
  
  return false;
}
```

### 3. Update Download
```typescript
// Send IPC message to main process
public async downloadUpdate(updateInfo: UpdateInfo): Promise<void> {
  ipcRenderer.send('download-update', updateInfo);
}
```

### 4. Installation
```typescript
// Install downloaded update
public async installUpdate(): Promise<void> {
  ipcRenderer.send('install-update');
}
```

## 🔧 Configuration

### Update Check Interval
```typescript
// Check every 60 minutes (default)
autoUpdater.startAutoUpdateCheck(60);

// Check every 30 minutes
autoUpdater.startAutoUpdateCheck(30);
```

### Notification Settings
```typescript
// Request notification permission
if ('Notification' in window) {
  Notification.requestPermission();
}

// Custom notification
new Notification('Data Studio Update Available', {
  body: `Version ${version} is available`,
  icon: '/favicon.ico'
});
```

## 📦 Release Process

### 1. Create New Version
```bash
# Bump version in package.json
npm version patch  # 1.0.0 → 1.0.1
npm version minor  # 1.0.0 → 1.1.0
npm version major  # 1.0.0 → 2.0.0
```

### 2. Create Git Tag
```bash
git tag -a v1.0.1 -m "Release v1.0.1: Bug fixes and improvements"
git push origin v1.0.1
```

### 3. Automated Build & Release
The GitHub Actions workflow automatically:
- Builds the application for all platforms
- Creates a GitHub release
- Uploads platform-specific installers
- Updates version numbers
- Generates release notes

### 4. User Experience
- Users receive notifications about available updates
- Updates download in the background
- Installation prompts when ready
- App restarts with new version

## 🛠️ Development

### Adding Update Features
```typescript
// Import the service
import AutoUpdaterService from '../services/AutoUpdater';

// Start auto-update checking
AutoUpdaterService.startAutoUpdateCheck();

// Listen for update events
AutoUpdaterService.onUpdateProgress((progress) => {
  console.log(`Download: ${progress.percent}%`);
});

AutoUpdaterService.onUpdateComplete(() => {
  console.log('Update downloaded successfully!');
});
```

### Custom Update Logic
```typescript
// Extend the service for custom behavior
class CustomAutoUpdater extends AutoUpdaterService {
  protected async checkForUpdates(): Promise<UpdateInfo | null> {
    // Custom update logic
    const customUpdate = await this.checkCustomSource();
    if (customUpdate) {
      return this.formatUpdateInfo(customUpdate);
    }
    return super.checkForUpdates();
  }
}
```

## 🔒 Security Considerations

### Update Verification
- All updates are downloaded from GitHub releases
- SHA256 checksums verify download integrity
- Code signing ensures authenticity
- HTTPS connections prevent tampering

### User Control
- Users can disable auto-updates
- Manual update checking available
- Update installation requires user consent
- Rollback to previous versions supported

## 📊 Monitoring & Analytics

### Update Metrics
- Update check frequency
- Download success rates
- Installation success rates
- User adoption rates

### Error Handling
- Network failure recovery
- Corrupted download detection
- Installation failure handling
- User notification of issues

## 🚀 Future Enhancements

### Planned Features
- **Delta Updates**: Download only changed files
- **Rollback Support**: Revert to previous versions
- **Update Scheduling**: Install updates at optimal times
- **Bandwidth Management**: Limit download speeds
- **Multi-Update Support**: Queue multiple updates

### Integration Options
- **Enterprise Repositories**: Private update servers
- **CDN Integration**: Faster download distribution
- **Analytics Dashboard**: Update statistics and insights
- **A/B Testing**: Gradual rollout of updates

## 📚 API Reference

### AutoUpdaterService Methods

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `startAutoUpdateCheck()` | Start automatic update checking | `intervalMinutes?: number` | `void` |
| `stopAutoUpdateCheck()` | Stop automatic update checking | None | `void` |
| `checkForUpdates()` | Manually check for updates | None | `Promise<UpdateInfo \| null>` |
| `downloadUpdate()` | Download available update | `updateInfo: UpdateInfo` | `Promise<void>` |
| `installUpdate()` | Install downloaded update | None | `Promise<void>` |

### Events

| Event | Description | Data |
|-------|-------------|------|
| `updateAvailable` | New update available | `UpdateInfo` |
| `update-progress` | Download progress | `UpdateProgress` |
| `update-complete` | Update downloaded | None |
| `update-error` | Update error occurred | `string` |

## 🤝 Contributing

### Adding New Platforms
1. Update the GitHub Actions workflow
2. Add platform-specific build scripts
3. Test the build process
4. Update documentation

### Improving Update Logic
1. Extend the AutoUpdaterService class
2. Add new update sources
3. Implement custom verification
4. Add comprehensive tests

### Bug Reports
Please report issues with:
- Detailed error messages
- Steps to reproduce
- Platform information
- App version

## 📄 License

This auto-updater system is part of Data Studio v2 and is licensed under the MIT License.

## 🔗 Related Documentation

- [Setup Guide](SETUP.md)
- [Cross-platform Build Guide](CROSS_PLATFORM_BUILD.md)
- [Integration Guide](INTEGRATION_GUIDE.md)
- [GitHub Repository](https://github.com/Raghavendra-Pratap/Data_Studio)

---

**Note**: This auto-updater system is designed to provide a seamless update experience while maintaining security and user control. All updates are verified and downloaded from trusted sources.
