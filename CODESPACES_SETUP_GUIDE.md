# 🚀 GitHub Codespaces Setup Guide

## 🎯 **Why Use GitHub Codespaces?**

✅ **No System Limitations**: Cloud-based development with full resources  
✅ **Consistent Environment**: Same setup across all devices  
✅ **Pre-configured Python**: All dependencies ready to go  
✅ **Integrated Development**: Full VS Code experience in browser  
✅ **GitHub Integration**: Direct access to your repository  
✅ **Professional Tools**: Pre-installed linting, formatting, testing  

## 🚀 **Quick Start (Recommended)**

### **Step 1: Open in Codespaces**
1. Go to `https://github.com/Raghavendra-Pratap/Plots`
2. Click the **Code** button (green button)
3. Select **Codespaces** tab
4. Click **Create codespace on main**

### **Step 2: Wait for Setup**
- Codespace will automatically:
  - Build the development container
  - Install all Python dependencies
  - Set up VS Code extensions
  - Configure the development environment

### **Step 3: Start Developing**
- Your code is ready in `/workspaces/Plots`
- All tools are pre-configured
- Start coding immediately!

## 🔧 **Manual Setup (Advanced)**

### **If you prefer manual control:**

1. **Clone the repository**
2. **Open in VS Code**
3. **Install Dev Containers extension**
4. **Reopen in container**

## 📁 **Codespace Environment Structure**

```
/workspaces/Plots/
├── .devcontainer/              # Container configuration
│   ├── devcontainer.json      # Main container config
│   └── setup.sh               # Setup script
├── bounding-box-plotter/       # Your BBP code
│   ├── bounding_box_plotter.py
│   ├── auto_updater.py
│   ├── version.py
│   ├── setup.py
│   ├── requirements.txt
│   ├── bounding_box_plotter.spec
│   ├── pyupdater.yml
│   ├── build.py
│   ├── README.md
│   ├── tests/
│   └── ...
├── README.md                   # Main repository README
└── LICENSE                     # Main repository license
```

## 🐍 **Pre-Installed Python Environment**

### **Python Version**: 3.11 (Latest Stable)
### **Pre-installed Packages**:
- **Core**: pandas, matplotlib, numpy, Pillow, requests, psutil
- **Development**: black, flake8, mypy, pytest, pre-commit
- **Building**: PyInstaller, setuptools, wheel, twine
- **Documentation**: sphinx, sphinx-rtd-theme

### **Virtual Environment**:
- Automatically created and activated
- Located at `/workspaces/Plots/venv`
- All packages installed in isolated environment

## 🛠️ **Pre-Configured Development Tools**

### **VS Code Extensions**:
- **Python**: Full Python support with IntelliSense
- **Pylint**: Code quality and error detection
- **Black**: Automatic code formatting
- **Flake8**: Style guide enforcement
- **MyPy**: Type checking
- **Pytest**: Testing framework
- **Pylance**: Advanced Python language server

### **Editor Settings**:
- **Format on Save**: Automatically format code
- **Auto-save**: Save files automatically
- **Import Organization**: Organize imports on save
- **Linting**: Real-time error detection

## 🚀 **Development Workflow in Codespaces**

### **1. Code Development**
```bash
# Navigate to your code
cd bounding-box-plotter

# Edit files directly in VS Code
# All changes are automatically saved
```

### **2. Testing**
```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=bounding_box_plotter --cov-report=html

# Run specific test
pytest tests/test_auto_updater.py -v
```

### **3. Code Quality**
```bash
# Format code
black bounding_box_plotter.py

# Check style
flake8 bounding_box_plotter.py

# Type checking
mypy bounding_box_plotter.py

# Run all quality checks
pre-commit run --all-files
```

### **4. Building**
```bash
# Build executable
python build.py --all

# Build specific platform
python build.py --windows
python build.py --macos
python build.py --linux

# Build Python package
python build.py --package
```

## 🔍 **Available Commands**

### **Development Commands**:
```bash
# Python
python --version
pip list
pip install package_name

# Git
git status
git add .
git commit -m "message"
git push origin main

# Testing
pytest
pytest -v
pytest --cov

# Code Quality
black .
flake8 .
mypy .
pre-commit run
```

### **System Commands**:
```bash
# System info
uname -a
df -h
free -h

# Process info
ps aux
top

# Network
curl -I https://github.com
wget https://example.com
```

## 📊 **Monitoring and Debugging**

### **Resource Usage**:
- **CPU**: Monitor with `top` or `htop`
- **Memory**: Check with `free -h`
- **Disk**: Monitor with `df -h`
- **Network**: Check with `netstat` or `ss`

### **Logs and Debugging**:
```bash
# View logs
tail -f logs/plotter.log

# Check Python path
python -c "import sys; print(sys.path)"

# Check installed packages
pip list | grep package_name

# Debug Python issues
python -v script.py
```

## 🔧 **Customization Options**

### **Modify Dev Container**:
1. Edit `.devcontainer/devcontainer.json`
2. Add/remove VS Code extensions
3. Change Python version
4. Add custom features

### **Add Custom Tools**:
1. Edit `.devcontainer/setup.sh`
2. Add package installations
3. Configure system settings
4. Set up custom scripts

### **Environment Variables**:
```json
"environmentVariables": {
    "PYTHONPATH": "/workspaces/Plots/bounding-box-plotter",
    "CUSTOM_VAR": "value"
}
```

## 🚨 **Troubleshooting**

### **Common Issues**:

#### **Codespace Won't Start**
- Check repository permissions
- Verify dev container configuration
- Check GitHub status

#### **Dependencies Not Installed**
- Run setup script manually: `bash .devcontainer/setup.sh`
- Check requirements.txt format
- Verify Python version compatibility

#### **VS Code Extensions Not Working**
- Reload VS Code window
- Check extension compatibility
- Verify container build success

#### **Build Failures**
- Check PyInstaller installation
- Verify system dependencies
- Check Python path configuration

### **Debug Commands**:
```bash
# Check container status
docker ps

# View container logs
docker logs container_name

# Enter container shell
docker exec -it container_name bash

# Check Python environment
which python
python -c "import sys; print(sys.executable)"
```

## 📱 **Accessing Your Codespace**

### **From GitHub**:
1. Repository → Code → Codespaces
2. Click existing codespace or create new

### **From VS Code**:
1. Install GitHub Codespaces extension
2. Command Palette → "Codespaces: Open in VS Code"
3. Select your codespace

### **From Browser**:
1. Direct URL: `https://github.com/codespaces`
2. Select your codespace
3. Opens in browser-based VS Code

## 🔄 **Syncing Changes**

### **Automatic Sync**:
- All changes are automatically saved
- Git integration works seamlessly
- Push/pull from any device

### **Manual Sync**:
```bash
# Pull latest changes
git pull origin main

# Push your changes
git add .
git commit -m "Update from Codespaces"
git push origin main
```

## 🎯 **Best Practices**

### **Development Workflow**:
1. **Always work in Codespaces** for consistency
2. **Use pre-commit hooks** for code quality
3. **Test before committing** with pytest
4. **Format code** with Black before saving
5. **Check types** with MyPy regularly

### **Resource Management**:
1. **Close unused Codespaces** to save resources
2. **Monitor resource usage** during builds
3. **Use appropriate machine size** for your needs
4. **Clean up temporary files** regularly

### **Collaboration**:
1. **Share Codespace URLs** with team members
2. **Use consistent development environment**
3. **Document custom configurations**
4. **Version control** all environment changes

## 🚀 **Next Steps**

### **Immediate Actions**:
1. **Open your repository in Codespaces**
2. **Verify the environment setup**
3. **Run a quick test** to ensure everything works
4. **Start developing** your Bounding Box Plotter!

### **Advanced Setup**:
1. **Customize the dev container** for your needs
2. **Add more development tools** as required
3. **Configure additional VS Code extensions**
4. **Set up automated testing** in your workflow

## 📞 **Support**

### **If you need help**:
1. **Check this guide** for common solutions
2. **Review GitHub Codespaces documentation**
3. **Check the troubleshooting section** above
4. **Create an issue** in your repository
5. **Contact maintainer**: contact@raghavendrapratap.com

---

**Happy Coding in the Cloud! 🚀☁️**

Your development environment is now completely cloud-based and ready for professional Python development! 