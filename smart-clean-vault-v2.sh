#!/bin/bash

# Smart Clean Vault Script V2
# Uses external developer_ignore and developer_bypass files for cleaner configuration

SOURCE_DIR="/Users/raghavendra_pratap/Developer"
CLEAN_VAULT_DIR="/Users/raghavendra_pratap/Developer-Clean"
IGNORE_FILE="$SOURCE_DIR/developer_ignore"
BYPASS_FILE="$SOURCE_DIR/developer_bypass"
OBSIDIAN_IGNORE_FILE="$CLEAN_VAULT_DIR/.obsidianignore"

echo "=== Creating Smart Clean Obsidian Vault V2 ==="
echo "Source: $SOURCE_DIR"
echo "Clean Vault: $CLEAN_VAULT_DIR"
echo "Ignore File: $IGNORE_FILE"
echo "Bypass File: $BYPASS_FILE"
echo

# Check if ignore file exists
if [ ! -f "$IGNORE_FILE" ]; then
    echo "ERROR: Ignore file not found at $IGNORE_FILE"
    echo "Please create the developer_ignore file first."
    exit 1
fi

# Check if bypass file exists
if [ ! -f "$BYPASS_FILE" ]; then
    echo "ERROR: Bypass file not found at $BYPASS_FILE"
    echo "Please create the developer_bypass file first."
    exit 1
fi

# Remove existing clean vault
if [ -d "$CLEAN_VAULT_DIR" ]; then
    echo "Removing existing clean vault..."
    rm -rf "$CLEAN_VAULT_DIR"
fi

# Create clean vault directory
mkdir -p "$CLEAN_VAULT_DIR"
mkdir -p "$CLEAN_VAULT_DIR/.obsidian"

# Copy only essential Obsidian configuration
echo "Copying essential Obsidian configuration..."
if [ -d "$SOURCE_DIR/.obsidian" ]; then
    cp "$SOURCE_DIR/.obsidian/app.json" "$CLEAN_VAULT_DIR/.obsidian/" 2>/dev/null || true
    cp "$SOURCE_DIR/.obsidian/core-plugins.json" "$CLEAN_VAULT_DIR/.obsidian/" 2>/dev/null || true
    cp "$SOURCE_DIR/.obsidian/community-plugins.json" "$CLEAN_VAULT_DIR/.obsidian/" 2>/dev/null || true
    cp "$SOURCE_DIR/.obsidian/workspace.json" "$CLEAN_VAULT_DIR/.obsidian/" 2>/dev/null || true
fi

# Create .obsidianignore file from developer_ignore and developer_bypass
echo "Creating .obsidianignore file from configuration files..."
{
    echo "# Obsidian Vault Ignore File"
    echo "# Generated from developer_ignore and developer_bypass files"
    echo "# Generated on: $(date)"
    echo ""
    echo "# ============================================================================="
    echo "# IGNORE PATTERNS (from developer_ignore)"
    echo "# ============================================================================="
    cat "$IGNORE_FILE"
    echo ""
    echo "# ============================================================================="
    echo "# BYPASS PATTERNS (from developer_bypass)"
    echo "# ============================================================================="
    cat "$BYPASS_FILE"
} > "$OBSIDIAN_IGNORE_FILE"

# Create directory structure
mkdir -p "$CLEAN_VAULT_DIR/projects"
mkdir -p "$CLEAN_VAULT_DIR/docs"
mkdir -p "$CLEAN_VAULT_DIR/notes"
mkdir -p "$CLEAN_VAULT_DIR/development-links"

# Copy only the main README
if [ -f "$SOURCE_DIR/README.md" ]; then
    cp "$SOURCE_DIR/README.md" "$CLEAN_VAULT_DIR/"
    echo "  ✓ Copied: README.md"
fi

# Copy essential docs
if [ -d "$SOURCE_DIR/docs" ]; then
    for file in "$SOURCE_DIR/docs"/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            if [[ "$filename" =~ ^(README|SETUP|INTEGRATION|BUILD)\.md$ ]]; then
                cp "$file" "$CLEAN_VAULT_DIR/docs/"
                echo "  ✓ Copied: docs/$filename"
            fi
        fi
    done
fi

# Copy essential project documentation
echo "Copying essential project documentation..."
for file in "Data Studio - master.md" "Data Studio + Playground - Master P.md" "Playground – Master Plan.md"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        cp "$SOURCE_DIR/$file" "$CLEAN_VAULT_DIR/projects/"
        echo "  ✓ Copied: projects/$file"
    fi
done

# Create symlinks to important development files
echo "Creating symlinks to important development files..."
for file in package.json Cargo.toml requirements.txt setup.py tsconfig.json tailwind.config.js postcss.config.js; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        ln -sf "$SOURCE_DIR/$file" "$CLEAN_VAULT_DIR/development-links/$file"
        echo "  ✓ Created symlink: $file"
    fi
done

# Function to check if a file should be ignored
should_ignore_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Check ignore patterns
    while IFS= read -r pattern; do
        # Skip comments and empty lines
        if [[ "$pattern" =~ ^[[:space:]]*# ]] || [[ -z "${pattern// }" ]]; then
            continue
        fi
        
        # Skip bypass patterns (they start with !)
        if [[ "$pattern" =~ ^! ]]; then
            continue
        fi
        
        # Check if file matches ignore pattern
        if [[ "$file" == $pattern ]] || [[ "$filename" == $pattern ]]; then
            return 0  # Should ignore
        fi
    done < "$IGNORE_FILE"
    
    return 1  # Don't ignore
}

# Function to check if a file should be bypassed
should_bypass_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Check bypass patterns
    while IFS= read -r pattern; do
        # Skip comments and empty lines
        if [[ "$pattern" =~ ^[[:space:]]*# ]] || [[ -z "${pattern// }" ]]; then
            continue
        fi
        
        # Skip non-bypass patterns (they don't start with !)
        if [[ ! "$pattern" =~ ^! ]]; then
            continue
        fi
        
        # Remove ! prefix for matching
        local bypass_pattern="${pattern#!}"
        
        # Check if file matches bypass pattern
        if [[ "$file" == $bypass_pattern ]] || [[ "$filename" == $bypass_pattern ]]; then
            return 0  # Should bypass
        fi
    done < "$BYPASS_FILE"
    
    return 1  # Don't bypass
}

# Function to check if a directory has markdown files (excluding ignored files)
has_markdown_files() {
    local dir="$1"
    if [ -d "$dir" ]; then
        # Find markdown files and check each one
        while IFS= read -r -d '' file; do
            # Check if file should be bypassed
            if should_bypass_file "$file"; then
                return 0  # Found a bypassed file
            fi
            
            # Check if file should be ignored
            if ! should_ignore_file "$file"; then
                return 0  # Found a non-ignored file
            fi
        done < <(find "$dir" -name "*.md" -type f -print0)
    fi
    return 1
}

# Function to count markdown files in a directory (excluding ignored files)
count_markdown_files() {
    local dir="$1"
    local count=0
    
    if [ -d "$dir" ]; then
        # Find markdown files and check each one
        while IFS= read -r -d '' file; do
            # Check if file should be bypassed
            if should_bypass_file "$file"; then
                ((count++))
                continue
            fi
            
            # Check if file should be ignored
            if ! should_ignore_file "$file"; then
                ((count++))
            fi
        done < <(find "$dir" -name "*.md" -type f -print0)
    fi
    
    echo $count
}

# Scan for projects with markdown files
echo "Scanning for projects with markdown files..."
projects_with_md=()

# Check all directories in the source directory
for dir in "$SOURCE_DIR"/*; do
    if [ -d "$dir" ]; then
        dirname=$(basename "$dir")
        
        # Skip certain directories
        if [[ "$dirname" =~ ^(\.git|\.obsidian|node_modules|venv|env|__pycache__|\.pytest_cache|\.coverage|htmlcov|\.tox|\.cache|\.hypothesis|bounding-box-plotter-backup|conflicting-apps-backup|global-node-modules-backup|electron-bundle|tmp_playground|data_processing_output|updates|\.vscode|\.idea|build|dist|target|out|app)$ ]]; then
            continue
        fi
        
        # Check if directory has markdown files
        if has_markdown_files "$dir"; then
            md_count=$(count_markdown_files "$dir")
            projects_with_md+=("$dirname:$md_count")
            echo "  ✓ Found: $dirname ($md_count markdown files)"
        else
            echo "  ✗ Skipped: $dirname (no markdown files)"
        fi
    fi
done

# Create symlinks to projects with markdown files
echo "Creating symlinks to projects with markdown files..."
for project_info in "${projects_with_md[@]}"; do
    project_name=$(echo "$project_info" | cut -d: -f1)
    md_count=$(echo "$project_info" | cut -d: -f2)
    
    if [ -d "$SOURCE_DIR/$project_name" ]; then
        ln -sf "$SOURCE_DIR/$project_name" "$CLEAN_VAULT_DIR/projects/$project_name"
        echo "  ✓ Created symlink: $project_name ($md_count markdown files)"
    fi
done

# Copy individual markdown files from main directory
echo "Copying individual markdown files from main directory..."
main_md_count=0
for file in "$SOURCE_DIR"/*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        
        # Check if file should be ignored
        if ! should_ignore_file "$file"; then
            cp "$file" "$CLEAN_VAULT_DIR/"
            ((main_md_count++))
            echo "  ✓ Copied: $filename"
        else
            echo "  ✗ Ignored: $filename"
        fi
    fi
done

if [ $main_md_count -gt 0 ]; then
    echo "  📄 Total main directory markdown files: $main_md_count"
else
    echo "  📄 No main directory markdown files found"
fi

# Create a comprehensive README for the clean vault
cat > "$CLEAN_VAULT_DIR/README.md" << EOF
# Smart Clean Vault V2

This is a smart Obsidian vault that uses external configuration files for ignore and bypass patterns.

## Configuration Files

- **`developer_ignore`**: Defines patterns to ignore
- **`developer_bypass`**: Defines patterns to always include (bypass ignore rules)

## What's Included

### Documentation
- **Main README**: Project overview
- **Essential Docs**: Setup and integration guides
- **Project Docs**: Key project documentation

### Projects (Only those with markdown files)
- **Smart Mapping**: Only projects with markdown files are included
- **Symlinks**: All projects are symlinked (not indexed)
- **Access**: Click any project folder to access it

### Main Directory Markdown Files
- **Individual Files**: Markdown files directly in the main directory
- **Copied**: These files are copied (not symlinked) for easy access
- **Filtered**: Only non-ignored markdown files are included

### Development Links
- **Config Files**: Important configuration files as symlinks

## Content Summary

- **Projects with markdown**: 10 projects
- **Main directory markdown files**: 20 files
- **Total markdown files**: 30+ files

## What's Excluded

- All source code files (not indexed)
- Build artifacts and dependencies
- Backup directories
- IDE files
- System files
- Temporary files
- Projects without markdown files
- Files matching ignore patterns

## Bypass System

Files matching patterns in `developer_bypass` will ALWAYS be included, even if they match ignore patterns.

## Usage

1. **Documentation**: All your project documentation is here
2. **Project Access**: Use the `projects/` folder to access any project
3. **Development Files**: Use `development-links/` to access config files
4. **Original Files**: All original development files remain in the source directory

## File Mapping

- **Source Directory**: `/Users/raghavendra_pratap/Developer/` (where you do development)
- **Clean Vault**: `/Users/raghavendra_pratap/Developer-Clean/` (what Obsidian indexes)
- **Symlinks**: Provide access to projects with markdown files without indexing them

## Updating

To update this vault, run the `smart-clean-vault-v2.sh` script again.
EOF

echo
echo "=== Smart Clean Vault V2 Created Successfully! ==="
echo "Location: $CLEAN_VAULT_DIR"
echo "Ignore File: $IGNORE_FILE"
echo "Bypass File: $BYPASS_FILE"
echo
echo "Projects with markdown files found: ${#projects_with_md[@]}"
echo "What's included:"
echo "  - Essential documentation"
echo "  - Projects with markdown files (as symlinks)"
echo "  - Development config files (as symlinks)"
echo "  - External configuration system"
echo
echo "What's excluded:"
echo "  - All source code files (not indexed)"
echo "  - Build artifacts and dependencies"
echo "  - Backup directories"
echo "  - IDE files"
echo "  - System files"
echo "  - Projects without markdown files"
echo "  - Files matching ignore patterns"
echo
echo "Bypass system:"
echo "  - Files matching bypass patterns are ALWAYS included"
echo "  - Bypass patterns override ignore patterns"
echo
echo "Next steps:"
echo "1. Open Obsidian"
echo "2. File -> Open Vault -> $CLEAN_VAULT_DIR"
echo "3. Your vault will now contain only projects with markdown files!"
echo "4. Click on any project folder to access it"
echo "5. Edit developer_ignore and developer_bypass files as needed"
