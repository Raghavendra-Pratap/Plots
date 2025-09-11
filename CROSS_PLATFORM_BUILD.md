# 🌍 Cross-Platform Build Guide - Unified Data Studio v2

## 🎯 **Multi-Platform Support**

Unified Data Studio v2 is designed to run on **all major platforms** with native performance and packaging.

## 🖥️ **Supported Platforms**

### **🍎 macOS**
- **Architectures**: Intel (x64) + Apple Silicon (ARM64)
- **Packages**: `.dmg` installer, `.zip` archive
- **Minimum**: macOS 10.15 (Catalina)

### **🐧 Linux**
- **Architectures**: x64, ARM64
- **Packages**: `.AppImage`, `.deb`, `.rpm`, `.snap`
- **Distributions**: Ubuntu, Debian, CentOS, Fedora, Arch

### **🪟 Windows**
- **Architectures**: x64, x86 (32-bit)
- **Packages**: `.exe` installer, `.msi` package, `.portable` zip
- **Minimum**: Windows 10

## 🚀 **Build Commands**

### **Build for All Platforms**
```bash
# Complete cross-platform build
npm run build:complete

# Or manually
npm run build:electron:all
```

### **Build for Specific Platform**
```bash
# macOS only
npm run build:electron:mac

# Linux only  
npm run build:electron:linux

# Windows only
npm run build:electron:win
```

### **Backend Cross-Compilation**
```bash
# For Linux (from macOS/Windows)
cd backend
rustup target add x86_64-unknown-linux-gnu
cargo build --release --target x86_64-unknown-linux-gnu

# For Windows (from macOS/Linux)
rustup target add x86_64-pc-windows-gnu
cargo build --release --target x86_64-pc-windows-gnu

# For macOS ARM (from Intel Mac)
rustup target add aarch64-apple-darwin
cargo build --release --target aarch64-apple-darwin
```

## 📦 **Package Types by Platform**

### **macOS Packages**
```bash
# DMG Installer (recommended)
unified-data-studio-v2-2.0.0-x64.dmg      # Intel Mac
unified-data-studio-v2-2.0.0-arm64.dmg    # Apple Silicon

# ZIP Archive (portable)
unified-data-studio-v2-2.0.0-x64.zip      # Intel Mac
unified-data-studio-v2-2.0.0-arm64.zip    # Apple Silicon
```

### **Linux Packages**
```bash
# AppImage (universal)
unified-data-studio-v2-2.0.0-x64.AppImage

# Debian/Ubuntu
unified-data-studio-v2_2.0.0_amd64.deb

# Red Hat/CentOS
unified-data-studio-v2-2.0.0.x86_64.rpm

# Snap (universal)
unified-data-studio-v2_2.0.0_amd64.snap
```

### **Windows Packages**
```bash
# Installer
unified-data-studio-v2 Setup 2.0.0.exe

# MSI Package
unified-data-studio-v2-2.0.0-x64.msi

# Portable
unified-data-studio-v2-2.0.0-portable.zip
```

## 🔧 **Build Configuration**

### **Electron Builder Config**
```json
{
  "build": {
    "mac": {
      "target": [
        { "target": "dmg", "arch": ["x64", "arm64"] },
        { "target": "zip", "arch": ["x64", "arm64"] }
      ]
    },
    "linux": {
      "target": [
        { "target": "AppImage", "arch": ["x64", "arm64"] },
        { "target": "deb", "arch": ["x64", "arm64"] },
        { "target": "rpm", "arch": ["x64", "arm64"] },
        { "target": "snap", "arch": ["x64", "arm64"] }
      ]
    },
    "win": {
      "target": [
        { "target": "nsis", "arch": ["x64", "ia32"] },
        { "target": "msi", "arch": ["x64", "ia32"] },
        { "target": "portable", "arch": ["x64", "ia32"] }
      ]
    }
  }
}
```

## 🐳 **Docker Build Environment**

### **Multi-Platform Docker Build**
```dockerfile
# Dockerfile for cross-platform builds
FROM rust:1.70 as rust-builder

# Install cross-compilation tools
RUN rustup target add x86_64-unknown-linux-gnu
RUN rustup target add x86_64-pc-windows-gnu
RUN rustup target add aarch64-apple-darwin

# Build for all targets
COPY . /app
WORKDIR /app/backend
RUN cargo build --release --target x86_64-unknown-linux-gnu
RUN cargo build --release --target x86_64-pc-windows-gnu
RUN cargo build --release --target aarch64-apple-darwin

# Node.js build stage
FROM node:18 as node-builder
COPY . /app
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Final stage
FROM node:18-alpine
COPY --from=rust-builder /app/backend/target/*/release/backend /usr/local/bin/
COPY --from=node-builder /app/frontend/build /app/build
COPY --from=node-builder /app/frontend/public/electron.js /app/

CMD ["/usr/local/bin/backend"]
```

### **Build Scripts**
```bash
#!/bin/bash
# build-all-platforms.sh

echo "🚀 Building for all platforms..."

# Build Rust backend for all targets
cd backend
cargo build --release --target x86_64-unknown-linux-gnu
cargo build --release --target x86_64-pc-windows-gnu
cargo build --release --target aarch64-apple-darwin
cd ..

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Build Electron packages
cd frontend
npm run build:electron:all
cd ..

echo "✅ Cross-platform build completed!"
```

## 📱 **Platform-Specific Features**

### **macOS Features**
- ✅ Native macOS UI/UX
- ✅ Apple Silicon optimization
- ✅ Gatekeeper compatibility
- ✅ Notarization support
- ✅ Spotlight integration

### **Linux Features**
- ✅ AppImage (universal)
- ✅ Package manager integration
- ✅ System tray support
- ✅ Desktop integration
- ✅ Multiple architectures

### **Windows Features**
- ✅ Windows installer
- ✅ MSI package support
- ✅ Portable mode
- ✅ Start menu integration
- ✅ Desktop shortcuts

## 🚨 **Common Cross-Platform Issues**

### **1. Architecture Mismatch**
```bash
# Check target architecture
rustup target list --installed

# Add missing target
rustup target add <target-triple>
```

### **2. Library Dependencies**
```bash
# Linux: Install development libraries
sudo apt-get install build-essential libssl-dev

# Windows: Use MSYS2/MinGW
pacman -S mingw-w64-x86_64-toolchain
```

### **3. Path Separators**
```rust
// Use platform-agnostic paths
use std::path::PathBuf;

let config_path = if cfg!(target_os = "windows") {
    PathBuf::from("C:\\ProgramData\\uds\\config.toml")
} else {
    PathBuf::from("/etc/uds/config.toml")
};
```

## 📊 **Build Performance**

### **Build Times (approximate)**
- **Single platform**: 2-3 minutes
- **All platforms**: 8-12 minutes
- **With Docker**: 15-20 minutes

### **Package Sizes**
- **macOS**: 25-35 MB
- **Linux**: 20-30 MB  
- **Windows**: 30-40 MB

## 🔄 **CI/CD Integration**

### **GitHub Actions Example**
```yaml
name: Cross-Platform Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest, windows-latest]
        rust: [stable, nightly]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Rust
      uses: actions-rs/toolchain@v1
      with:
        toolchain: ${{ matrix.rust }}
    
    - name: Build Backend
      run: |
        cd backend
        cargo build --release
    
    - name: Build Frontend
      run: |
        cd frontend
        npm install
        npm run build
    
    - name: Build Electron Package
      run: |
        cd frontend
        npm run build:electron:${{ matrix.os }}
```

## 🎯 **Distribution Strategy**

### **1. Platform-Specific Downloads**
- Provide appropriate package for user's OS
- Auto-detect architecture
- Show download progress

### **2. Universal Packages**
- AppImage for Linux (runs everywhere)
- Portable ZIP for Windows
- DMG for macOS

### **3. Package Managers**
- Homebrew for macOS
- Snap/Flatpak for Linux
- Chocolatey for Windows

## 🚀 **Next Steps**

1. **Test on target platforms**
2. **Set up CI/CD pipeline**
3. **Create distribution website**
4. **Implement auto-updates**
5. **Add platform-specific optimizations**

---

**🌍 Build once, run everywhere! Unified Data Studio v2 supports all major platforms with native performance.**
