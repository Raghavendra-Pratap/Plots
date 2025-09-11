# 🚀 Unified Data Studio v2 - Setup Guide

## 📋 Prerequisites

### System Requirements
- **Windows**: Windows 10/11 (64-bit)
- **macOS**: macOS 10.15+ (Intel/Apple Silicon)
- **Linux**: Ubuntu 18.04+, CentOS 7+, or compatible distributions

### Hardware Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB available space
- **Processor**: Multi-core CPU (2+ cores recommended)

## 🪟 Windows Installation

### Option 1: Executable Installer (Recommended)
1. Download `Unified.Data.Studio.Setup.v2.x.x.exe`
2. Run the installer as Administrator
3. Follow the installation wizard
4. Launch from Start Menu or Desktop shortcut

### Option 2: Portable Version
1. Download the ZIP archive
2. Extract to your preferred location
3. Run `Unified.Data.Studio.exe` directly

## 🍎 macOS Installation

### Option 1: DMG Package (Recommended)
1. Download `Unified.Data.Studio-v2.x.x.dmg`
2. Double-click the DMG file
3. Drag the app to Applications folder
4. Launch from Applications or Spotlight

### Option 2: Homebrew (Advanced Users)
```bash
brew install --cask unified-data-studio
```

## 🐧 Linux Installation

### Option 1: AppImage (Recommended)
1. Download `Unified.Data.Studio-v2.x.x.AppImage`
2. Make executable: `chmod +x Unified.Data.Studio-v2.x.x.AppImage`
3. Run: `./Unified.Data.Studio-v2.x.x.AppImage`

### Option 2: Package Manager
```bash
# Ubuntu/Debian
sudo apt install ./unified-data-studio-v2.x.x.deb

# CentOS/RHEL
sudo yum install ./unified-data-studio-v2.x.x.rpm
```

## 🔧 First Launch Setup

1. **Launch the application**
2. **Accept license agreement**
3. **Choose installation directory** (if prompted)
4. **Configure initial settings**
5. **Import existing data** (optional)

## ⚙️ Configuration

### Data Directory
- **Default**: `~/Documents/UnifiedDataStudio/`
- **Custom**: Set in Settings → Data → Storage Location

### Database Setup
- **SQLite**: Automatically configured
- **External**: Configure in Settings → Database

### Theme & Appearance
- **Light/Dark Mode**: Settings → Appearance → Theme
- **Language**: Settings → General → Language

## 🔄 Updates

### Automatic Updates
- Updates are checked automatically
- Notifications appear when new versions are available
- One-click update installation

### Manual Updates
1. Download new version from GitHub Releases
2. Install over existing installation
3. Data is preserved automatically

## 🚨 Troubleshooting

### Common Issues

#### Installation Fails
- **Windows**: Run as Administrator
- **macOS**: Allow apps from unidentified developers
- **Linux**: Check file permissions and dependencies

#### App Won't Launch
- Check system requirements
- Verify installation integrity
- Check error logs in `~/Library/Logs/` (macOS) or `~/.local/share/`

#### Performance Issues
- Close other applications
- Check available RAM
- Verify disk space

### Getting Help
- **GitHub Issues**: [Report bugs here](https://github.com/Raghavendra-Pratap/Data_Studio/issues)
- **Documentation**: Check other guides in this repository
- **Community**: Join our discussions

## 📚 Next Steps

After installation:
1. Read the [Integration Guide](INTEGRATION.md)
2. Explore the [Build Guide](BUILD.md) for developers
3. Check out sample data and workflows
4. Join our community for support

---

*For developers and contributors, see [BUILD.md](BUILD.md)*
