# 🏗️ Unified Data Studio v2 - Build Guide

## 📋 Overview

This guide covers building Unified Data Studio v2 from source code for development, testing, and distribution.

## 🛠️ Prerequisites

### Required Software
- **Node.js**: 18.x or higher
- **Rust**: 1.70+ (stable toolchain)
- **Python**: 3.9+
- **Git**: Latest version
- **Build Tools**: Platform-specific

### Platform-Specific Requirements

#### Windows
```bash
# Install Visual Studio Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools
# or download from Microsoft's website

# Install Rust
winget install Rust.Rust
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

#### Linux (Ubuntu/Debian)
```bash
# Install build essentials
sudo apt update
sudo apt install build-essential pkg-config libssl-dev

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Raghavendra-Pratap/Data_Studio.git
cd Data_Studio
git checkout develop
```

### 2. Install Dependencies
```bash
# Frontend dependencies
cd frontend
npm ci

# Backend dependencies
cd ../backend
cargo build

# Python dependencies
cd ..
pip install -r requirements.txt
```

### 3. Build Project
```bash
# Use the build script
python build_complete_package.py
```

## 🏗️ Detailed Build Process

### Frontend Build (React + Electron)

#### Development Mode
```bash
cd frontend
npm run dev          # Start React dev server
npm run electron     # Start Electron in dev mode
```

#### Production Build
```bash
cd frontend
npm run build        # Build React app
npm run electron:build  # Build Electron app
```

#### Platform-Specific Builds
```bash
# Windows
npm run electron:build -- --win

# macOS
npm run electron:build -- --mac

# Linux
npm run electron:build -- --linux
```

### Backend Build (Rust)

#### Development
```bash
cd backend
cargo build          # Debug build
cargo run            # Run with hot reload
```

#### Production
```bash
cd backend
cargo build --release  # Optimized build
cargo test            # Run tests
```

#### Cross-Compilation
```bash
# For Windows from Linux/macOS
rustup target add x86_64-pc-windows-gnu
cargo build --target x86_64-pc-windows-gnu --release

# For macOS from Linux
rustup target add x86_64-apple-darwin
cargo build --target x86_64-apple-darwin --release
```

### Python Integration

#### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Build Script
```bash
# Run build script
python build_complete_package.py

# Validate only (no build)
python build_complete_package.py --validate-only
```

## 🔧 Configuration

### Environment Variables
```bash
# Development
export NODE_ENV=development
export RUST_LOG=debug
export PYTHONPATH=.

# Production
export NODE_ENV=production
export RUST_LOG=info
```

### Build Configuration

#### Frontend (package.json)
```json
{
  "build": {
    "appId": "com.unifieddatastudio.app",
    "productName": "Unified Data Studio v2",
    "directories": {
      "output": "dist"
    }
  }
}
```

#### Backend (Cargo.toml)
```toml
[package]
name = "unified-data-studio-backend"
version = "2.0.0"
edition = "2021"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
```

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm test              # Run Jest tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report
```

### Backend Tests
```bash
cd backend
cargo test            # Run all tests
cargo test --release  # Release mode tests
cargo bench           # Benchmarks
```

### Integration Tests
```bash
# Run the complete validation
python build_complete_package.py --validate-only

# Run specific test suites
python -m pytest tests/
```

## 📦 Packaging

### Complete Package Build
```bash
# Build everything
python build_complete_package.py

# Output locations:
# - frontend/dist/ (Electron apps)
# - backend/target/release/ (Rust binaries)
# - build/ (Combined packages)
```

### Platform-Specific Packages

#### Windows
- **Installer**: `.exe` (NSIS)
- **Portable**: `.zip`
- **MSI**: `.msi` (if configured)

#### macOS
- **DMG**: `.dmg` (disk image)
- **PKG**: `.pkg` (installer package)
- **ZIP**: `.zip` (portable)

#### Linux
- **AppImage**: `.AppImage` (portable)
- **DEB**: `.deb` (Debian/Ubuntu)
- **RPM**: `.rpm` (Red Hat/CentOS)

## 🚀 CI/CD Integration

### GitHub Actions
The project includes automated workflows:
- **CI**: Cross-platform testing
- **Pre-Release Validation**: Quality checks
- **Release**: Automated packaging and distribution

### Local CI Simulation
```bash
# Run validation locally
python build_complete_package.py --validate-only

# Test cross-platform builds
./scripts/test-cross-platform.sh
```

## 🔍 Debugging

### Common Build Issues

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm ci
```

#### Rust Issues
```bash
# Update Rust toolchain
rustup update

# Clean and rebuild
cargo clean
cargo build
```

#### Python Issues
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Logs and Debugging
```bash
# Frontend logs
tail -f ~/.config/UnifiedDataStudio/logs/frontend.log

# Backend logs
tail -f ~/.config/UnifiedDataStudio/logs/backend.log

# Build logs
tail -f build.log
```

## 📚 Additional Resources

- [Setup Guide](SETUP.md) - User installation guide
- [Integration Guide](INTEGRATION.md) - API and integration details
- [GitHub Repository](https://github.com/Raghavendra-Pratap/Data_Studio)
- [Issues & Discussions](https://github.com/Raghavendra-Pratap/Data_Studio/issues)

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Create Pull Request

### Code Standards
- **Frontend**: ESLint + Prettier
- **Backend**: Rustfmt + Clippy
- **Python**: Black + Flake8
- **Commits**: Conventional Commits

---

*For user setup, see [SETUP.md](SETUP.md)*
