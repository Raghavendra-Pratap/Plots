# home_page.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QSizePolicy
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Studio - Home")
        self.resize(1200, 800)
        self.setup_ui()

    def setup_ui(self):
        # Main horizontal layout → Sidebar + Main Content
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

        # Main content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Header (Title + New Project Button)
        header_layout = QHBoxLayout()
        title_label = QLabel("Data Studio")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        new_project_button = QPushButton("+ New Project")
        new_project_button.setFixedHeight(40)
        new_project_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(new_project_button)
        content_layout.addLayout(header_layout)

        # Top cards (Active Projects, Processed Files, Data Volume)
        cards_layout = QHBoxLayout()
        cards = ["Active Projects", "Processed Files", "Data Volume"]
        for card_title in cards:
            card = QLabel(card_title)
            card.setStyleSheet("""
                QLabel {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 30px;
                    font-size: 18px;
                    font-weight: bold;
                    min-width: 200px;
                    text-align: center;
                }
            """)
            card.setAlignment(Qt.AlignCenter)
            cards_layout.addWidget(card)

        content_layout.addLayout(cards_layout)

        # Middle section (Recent Projects and Recent Activity + Quick Actions)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)

        # Recent Projects Section
        recent_projects_label = QLabel("Recent Projects")
        recent_projects_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 20px;
                font-size: 20px;
                font-weight: bold;
                min-height: 300px;
            }
        """)
        recent_projects_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        middle_layout.addWidget(recent_projects_label, 2)

        # Right side layout (Recent Activity + Quick Actions)
        right_side_layout = QVBoxLayout()
        right_side_layout.setSpacing(20)

        # Recent Activity Section
        recent_activity_label = QLabel("Recent Activities")
        recent_activity_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 20px;
                font-size: 20px;
                font-weight: bold;
                min-height: 150px;
            }
        """)
        recent_activity_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        right_side_layout.addWidget(recent_activity_label)

        # Quick Actions Section
        quick_actions_label = QLabel("Quick Actions")
        quick_actions_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 20px;
                font-size: 20px;
                font-weight: bold;
                min-height: 150px;
            }
        """)
        quick_actions_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        right_side_layout.addWidget(quick_actions_label)

        middle_layout.addLayout(right_side_layout, 1)

        content_layout.addLayout(middle_layout)

        # Content container widget
        content_widget = QWidget()
        content_widget.setLayout(content_layout)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(content_widget)

# 🔥 Test Mode
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec_())