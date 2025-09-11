# workspace_page.py

import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QFileDialog, QListWidget, QListWidgetItem,
    QTextEdit, QSizePolicy, QScrollArea, QFrame
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

class DragDropArea(QLabel):
    def __init__(self, on_files_dropped):
        super().__init__()
        self.setText("📂 Drop Files Here\n(Support for CSV, Excel files)")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #bbb;
                border-radius: 10px;
                background-color: #fafafa;
                font-size: 18px;
                color: #888;
                padding: 40px;
                text-align: center;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.on_files_dropped = on_files_dropped

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.on_files_dropped(files)

class WorkspacePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Studio - Workspace")
        self.resize(1400, 900)
        self.files = []
        self.file_details = {}  # Store file metadata
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(10, 20, 10, 10)
        sidebar.setSpacing(20)

        buttons = [
            ("Home", QIcon.fromTheme("go-home")),
            ("Workspace", QIcon.fromTheme("folder")),
            ("Projects", QIcon.fromTheme("folder-open")),
            ("Notifications", QIcon.fromTheme("mail-unread")),
            ("Settings", QIcon.fromTheme("preferences-system")),
        ]

        for text, icon in buttons:
            btn = QPushButton()
            btn.setIcon(icon)
            btn.setIconSize(QSize(32, 32))
            btn.setFixedSize(60, 60)
            btn.setToolTip(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border-radius: 10px;
                }
            """)
            sidebar.addWidget(btn)

        sidebar.addStretch()

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(80)

        # Right Content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        breadcrumb = QLabel("Data Studio > Workspace")
        breadcrumb.setStyleSheet("font-size: 20px; font-weight: bold;")
        new_project_btn = QPushButton("+ New Project")
        new_project_btn.setFixedHeight(40)
        new_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        header_layout.addWidget(breadcrumb)
        header_layout.addStretch()
        header_layout.addWidget(new_project_btn)
        content_layout.addLayout(header_layout)

        # Top Menu Tabs
        menu_layout = QHBoxLayout()
        tabs = ["Import", "Clean", "Transform", "Analyze", "Template", "Export"]
        for tab_name in tabs:
            tab_btn = QPushButton(tab_name)
            tab_btn.setFixedHeight(40)
            tab_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    color: #333;
                    font-size: 16px;
                    padding: 8px 12px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #ddd;
                }
            """)
            menu_layout.addWidget(tab_btn)
        content_layout.addLayout(menu_layout)

        # Split Area: Data Source | DragDrop | Properties
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

        # Data Source List
        self.data_sources = QListWidget()
        self.data_sources.setFixedWidth(200)
        self.data_sources.setStyleSheet("""
            QListWidget {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        split_layout.addWidget(self.data_sources)

        # Drag and Drop Area
        self.drag_drop_area = DragDropArea(self.handle_files_dropped)
        split_layout.addWidget(self.drag_drop_area, 2)

        # Properties Panel
        self.properties_panel = QTextEdit()
        self.properties_panel.setReadOnly(True)
        self.properties_panel.setFixedWidth(250)
        self.properties_panel.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
        """)
        split_layout.addWidget(self.properties_panel)

        content_layout.addLayout(split_layout)

        # File Preview Area
        preview_title = QLabel("File Preview")
        preview_title.setStyleSheet("font-size: 22px; font-weight: bold; margin-top: 10px;")
        content_layout.addWidget(preview_title)

        # Scrollable Preview Panel
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)

        self.preview_container = QWidget()
        self.preview_layout = QHBoxLayout()
        self.preview_layout.setContentsMargins(10, 10, 10, 10)
        self.preview_container.setLayout(self.preview_layout)

        self.preview_scroll.setWidget(self.preview_container)
        content_layout.addWidget(self.preview_scroll)

        # Proceed Button
        proceed_button = QPushButton("Proceed")
        proceed_button.setFixedHeight(50)
        proceed_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        content_layout.addWidget(proceed_button)

        # Assemble
        content_widget = QWidget()
        content_widget.setLayout(content_layout)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(content_widget)

    def handle_files_dropped(self, file_paths):
        for file_path in file_paths:
            if file_path not in self.files:
                self.files.append(file_path)
                self.data_sources.addItem(QListWidgetItem(os.path.basename(file_path)))
                self.analyze_file(file_path)

    def analyze_file(self, file_path):
        file_info = {
            "type": "",
            "columns": [],
            "rows": 0,
            "size": os.path.getsize(file_path) / 1024  # size in KB
        }
        try:
            if file_path.lower().endswith(".csv"):
                df = pd.read_csv(file_path)
                file_info["type"] = "CSV"
            elif file_path.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(file_path)
                file_info["type"] = "Excel"
            else:
                df = pd.DataFrame()
                file_info["type"] = "Unknown"

            file_info["columns"] = list(df.columns)
            file_info["rows"] = df.shape[0]
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            file_info["type"] = "Unreadable"
            file_info["columns"] = []
            file_info["rows"] = 0

        self.file_details[file_path] = file_info
        self.update_properties(file_path)
        self.update_preview()

    def update_properties(self, file_path):
        info = self.file_details[file_path]
        properties_text = f"""File: {os.path.basename(file_path)}
Type: {info['type']}
Columns: {len(info['columns'])}
Rows: {info['rows']}
Size: {info['size']:.2f} KB
"""
        self.properties_panel.setPlainText(properties_text)

    def update_preview(self):
        # Clear previous previews
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for file_path, info in self.file_details.items():
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setStyleSheet("""
                QFrame {
                    background-color: #fafafa;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    min-width: 250px;
                }
            """)
            layout = QVBoxLayout()

            title = QLabel(f"{os.path.basename(file_path)} ({len(info['columns'])} columns)")
            title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
            layout.addWidget(title)

            for col in info["columns"]:
                col_label = QLabel(f"• {col}")
                layout.addWidget(col_label)

            frame.setLayout(layout)
            self.preview_layout.addWidget(frame)

# 🔥 Test Mode
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkspacePage()
    window.show()
    sys.exit(app.exec_())