# components/sidebar.py
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QToolTip
import qtawesome as qta

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedWidth(80)  # Sidebar width
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(10, 30, 10, 10)

        # Icon buttons
        self.home_button = self.create_icon_button('fa.home', 'Home')
        self.workspace_button = self.create_icon_button('fa.archive', 'Workspace')
        self.projects_button = self.create_icon_button('fa.folder-open', 'Projects')
        self.notifications_button = self.create_icon_button('fa.bell', 'Notifications')
        self.settings_button = self.create_icon_button('fa.cog', 'Settings')

        # Add to layout
        layout.addWidget(self.home_button)
        layout.addWidget(self.workspace_button)
        layout.addWidget(self.projects_button)
        layout.addWidget(self.notifications_button)
        layout.addWidget(self.settings_button)

        layout.addStretch()

        self.setLayout(layout)

    def create_icon_button(self, icon_name, tooltip_text):
        button = QPushButton()
        button.setIcon(qta.icon(icon_name, color='gray'))
        button.setIconSize(QtCore.QSize(32, 32))
        button.setFixedSize(60, 60)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 10px;
            }
        """)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setToolTip(tooltip_text)
        return button