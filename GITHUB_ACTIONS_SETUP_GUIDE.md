# 🚀 GitHub Actions Setup Guide for Plots Repository

This guide will help you set up the automated CI/CD pipeline in your `Raghavendra-Pratap/Plots` repository.

## 📋 Prerequisites

Before setting up GitHub Actions, ensure you have:

1. **Repository Access**: Admin access to `https://github.com/Raghavendra-Pratap/Plots`
2. **Git Installed**: Git command line tools on your local machine
3. **Python Knowledge**: Basic understanding of Python and pip

## 🏗️ Repository Structure Setup

### Step 1: Create the Directory Structure

```bash
# Clone your repository
git clone https://github.com/Raghavendra-Pratap/Plots.git
cd Plots

# Create the bounding-box-plotter directory
mkdir bounding-box-plotter

# Copy all BBP files into this directory
# (You'll do this in the next step)
```

### Step 2: Copy All BBP Files

Copy all the files from your current BBP directory into `Plots/bounding-box-plotter/`:

```
Plots/
├── .github/                     # GitHub Actions workflows
│   └── workflows/
│       └── build.yml
├── bounding-box-plotter/        # Your BBP code
│   ├── bounding_box_plotter.py
│   ├── auto_updater.py
│   ├── version.py
│   ├── setup.py
│   ├── requirements.txt
│   ├── bounding_box_plotter.spec
│   ├── pyupdater.yml
│   ├── build.py
│   ├── README.md
│   ├── LICENSE
│   ├── CONTRIBUTING.md
│   ├── CHANGELOG.md
│   ├── tests/
│   │   └── test_auto_updater.py
│   ├── pytest.ini
│   └── .gitignore
├── README.md                    # Main repository README
└── LICENSE                      # Main repository license
```

## 🔧 GitHub Actions Configuration

### Step 3: Create the .github Directory

```bash
# In your Plots repository
mkdir -p .github/workflows
```

### Step 4: Copy the Workflow File

Copy the updated `build.yml` file to `.github/workflows/build.yml`. The file has been updated to work with your repository structure.

### Step 5: Verify Workflow Configuration

The workflow file should contain these key sections:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

jobs:
  test:
    # ... testing configuration
    
  build:
    # ... building configuration
    
  release:
    # ... release configuration
    
  publish-pypi:
    # ... PyPI publishing configuration
```

## 🚀 Setting Up the Workflow

### Step 6: Push to GitHub

```bash
# Add all files
git add .

# Commit the changes
git commit -m "Add Bounding Box Plotter with GitHub Actions workflow"

# Push to main branch
git push origin main
```

### Step 7: Verify Workflow Creation

1. Go to your repository: `https://github.com/Raghavendra-Pratap/Plots`
2. Click on the **Actions** tab
3. You should see the "Build and Release" workflow
4. The workflow will automatically run on the first push

## 🧪 Testing the Workflow

### Step 8: Test the Testing Job

Create a test commit to trigger the workflow:

```bash
# Make a small change
echo "# Test commit" >> README.md

# Commit and push
git add README.md
git commit -m "Test GitHub Actions workflow"
git push origin main
```

**Expected Result**: The workflow should run and execute the testing job successfully.

### Step 9: Test the Building Job

The building job only runs after successful testing, so if the testing job passes, the building job should also work.

## 🏷️ Creating Your First Release

### Step 10: Update Version

```bash
# Edit the version file
cd bounding-box-plotter
# Update version.py to your desired version (e.g., 2.0.0)
```

### Step 11: Create and Push Tag

```bash
# Create a version tag
git tag v2.0.0

# Push the tag
git push origin v2.0.0
```

**Expected Result**: 
1. The workflow will automatically run
2. All jobs (test, build, release) will execute
3. A GitHub release will be created
4. Assets will be uploaded to the release
5. PyPI package will be published (if configured)

## ⚙️ Configuration Options

### Environment Variables

You may need to set up these secrets in your repository:

1. **Go to**: `Settings` → `Secrets and variables` → `Actions`
2. **Add these secrets**:

#### For PyPI Publishing:
```
PYPI_API_TOKEN = your_pypi_token_here
```

#### For Code Coverage (Optional):
```
CODECOV_TOKEN = your_codecov_token_here
```

### Workflow Customization

You can customize the workflow by editing `.github/workflows/build.yml`:

#### Change Python Versions:
```yaml
python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
```

#### Change Build Platforms:
```yaml
runs-on: ${{ matrix.os }}
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
```

#### Change Update Frequency:
```yaml
# In the workflow triggers
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Workflow Not Running
**Problem**: Workflow doesn't start after push
**Solution**: 
- Check if `.github/workflows/build.yml` exists
- Verify YAML syntax is correct
- Check repository permissions

#### Issue 2: Tests Failing
**Problem**: Testing job fails
**Solution**:
- Check if all dependencies are in `requirements.txt`
- Verify test files are in the correct location
- Check Python version compatibility

#### Issue 3: Build Failing
**Problem**: Building job fails
**Solution**:
- Check if PyInstaller is installed
- Verify the spec file path is correct
- Check platform-specific requirements

#### Issue 4: Release Not Created
**Problem**: Release job doesn't run
**Solution**:
- Ensure you're pushing a tag (not just a commit)
- Check if the tag format is `v*` (e.g., v2.0.0)
- Verify repository permissions

### Debugging Commands

```bash
# Check workflow status
gh run list

# View workflow logs
gh run view <run_id>

# Rerun failed workflow
gh run rerun <run_id>
```

## 📊 Monitoring and Analytics

### Workflow Metrics

Monitor your workflow performance:

1. **Success Rate**: Check how often builds succeed
2. **Build Time**: Monitor how long builds take
3. **Resource Usage**: Track GitHub Actions minutes used
4. **Error Patterns**: Identify common failure points

### Performance Optimization

```yaml
# Add caching to speed up builds
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## 🔮 Advanced Features

### Conditional Workflows

```yaml
# Only run on specific branches
if: github.ref == 'refs/heads/main'

# Only run on specific file changes
paths:
  - 'bounding-box-plotter/**'
  - '.github/workflows/**'
```

### Matrix Builds

```yaml
# Build for multiple Python versions and platforms
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11']
    os: [ubuntu-latest, windows-latest, macos-latest]
```

### Scheduled Workflows

```yaml
# Run workflow automatically
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

## 📚 Additional Resources

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)

### Community
- [GitHub Actions Community](https://github.com/actions/community)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/github-actions)

## 🎯 Next Steps

After setting up the workflow:

1. **Test thoroughly** with small commits
2. **Create your first release** with a version tag
3. **Monitor performance** and optimize as needed
4. **Add more tools** to your Plots suite
5. **Expand the workflow** for additional features

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Review GitHub Actions logs** for detailed error messages
3. **Create an issue** in your repository
4. **Contact maintainer**: contact@raghavendrapratap.com

---

**Happy Building! 🚀**

Your Plots repository is now set up with a professional CI/CD pipeline that will automatically test, build, and release your tools. 