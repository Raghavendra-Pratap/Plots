import os

# Define the folders and files
folders = [
    "DataStudio/pages",
    "DataStudio/components",
    "DataStudio/assets/icons",
    "DataStudio/utils",
    "DataStudio/data"
]

files = {
    "DataStudio/main.py": "",
    "DataStudio/README.md": "",
    "DataStudio/pages/home_page.py": "",
    "DataStudio/pages/workspace_page.py": "",
    "DataStudio/pages/playground_page.py": "",
    "DataStudio/pages/projects_page.py": "",
    "DataStudio/pages/analytics_page.py": "",
    "DataStudio/pages/settings_page.py": "",
    "DataStudio/pages/notifications_page.py": "",
    "DataStudio/components/sidebar.py": "",
    "DataStudio/components/header.py": "",
    "DataStudio/components/card.py": "",
    "DataStudio/components/file_preview.py": "",
    "DataStudio/utils/file_utils.py": "",
    "DataStudio/utils/logger.py": "",
    "DataStudio/data/sample_data.csv": ""
}

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create files
for file_path, content in files.items():
    with open(file_path, "w") as f:
        f.write(content)

print("✅ Project structure created successfully!")