#!/usr/bin/env python3
"""
Main Window Component for Unified Data Studio
Professional data studio interface with modern design
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QPushButton, QLabel, QSplitter, QFrame, QScrollArea,
    QSizePolicy, QMenuBar, QStatusBar, QToolBar, QMenu,
    QTableWidget, QTableWidgetItem, QTextEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton,
    QGroupBox, QFormLayout, QGridLayout, QStackedWidget,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QSlider, QDial, QCalendarWidget, QDateEdit,
    QTimeEdit, QDateTimeEdit, QLineEdit, QTextEdit, QPlainTextEdit,
    QFileDialog, QColorDialog, QFontDialog, QInputDialog,
    QMessageBox, QToolButton, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QRect
from PySide6.QtGui import QIcon, QFont, QPixmap, QAction, QPalette, QColor, QPainter, QBrush, QPen

# Import our components
from .playground import Playground
from .projects import Projects
from .workflows import Workflows
from .analytics import Analytics
from .settings import Settings
from .notifications import Notifications

class ModernFrame(QFrame):
    """Modern styled frame with rounded corners and shadow"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("""
            ModernFrame {
                background-color: #ffffff;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                padding: 8px;
            }
        """)

class DataStudioTab(QWidget):
    """Base class for all data studio tabs with consistent styling"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the tab UI - to be overridden by subclasses"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("SF Pro Display", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Content placeholder
        content_label = QLabel(f"Welcome to {self.title}")
        content_label.setFont(QFont("SF Pro Text", 14))
        content_label.setStyleSheet("color: #7f8c8d;")
        content_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(content_label)
        
        layout.addStretch()

class MainWindow(QWidget):
    """Main application window with professional data studio interface"""
    
    # Signals
    file_imported = Signal(str)
    workflow_executed = Signal(str)
    project_created = Signal(str)
    
    def __init__(self, duckdb_service=None, data_service=None, workflow_service=None):
        super().__init__()
        
        # Store backend services
        self.duckdb_service = duckdb_service
        self.data_service = data_service
        self.workflow_service = workflow_service
        
        # Initialize UI
        self.setup_ui()
        self.setup_connections()
        self.apply_styling()
        
        # Setup status updates
        self.setup_status_updates()
    
    def setup_ui(self):
        """Setup the main user interface with professional layout"""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create right panel
        self.create_right_panel()
    
    def create_sidebar(self):
        """Create the left sidebar with navigation"""
        sidebar = ModernFrame()
        sidebar.setMaximumWidth(250)
        sidebar.setMinimumWidth(200)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        
        # Logo/Title
        logo_frame = QFrame()
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(0, 0, 0, 20)
        
        logo_label = QLabel("📊")
        logo_label.setFont(QFont("SF Pro Display", 24))
        logo_layout.addWidget(logo_label)
        
        title_label = QLabel("Data Studio")
        title_label.setFont(QFont("SF Pro Display", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        logo_layout.addWidget(title_label)
        
        sidebar_layout.addWidget(logo_frame)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", "dashboard"),
            ("📁 Projects", "projects"),
            ("🔧 Workflows", "workflows"),
            ("📊 Analytics", "analytics"),
            ("⚙️ Settings", "settings"),
            ("🔔 Notifications", "notifications")
        ]
        
        for text, action in nav_buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("SF Pro Text", 12))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    text-align: left;
                    padding: 12px 15px;
                    border-radius: 6px;
                    color: #5a6c7d;
                }
                QPushButton:hover {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                }
                QPushButton:pressed {
                    background-color: #e9ecef;
                }
            """)
            btn.clicked.connect(lambda checked, a=action: self.navigate_to(a))
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # User section
        user_frame = QFrame()
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(0, 20, 0, 0)
        
        user_avatar = QLabel("👤")
        user_avatar.setFont(QFont("SF Pro Display", 16))
        user_layout.addWidget(user_avatar)
        
        user_info = QLabel("User")
        user_info.setFont(QFont("SF Pro Text", 12))
        user_info.setStyleSheet("color: #5a6c7d;")
        user_layout.addWidget(user_info)
        
        sidebar_layout.addWidget(user_frame)
        
        main_layout.addWidget(sidebar)
    
    def create_main_content(self):
        """Create the main content area"""
        content_frame = ModernFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Header with breadcrumbs and actions
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Breadcrumbs
        breadcrumb_label = QLabel("Dashboard > Overview")
        breadcrumb_label.setFont(QFont("SF Pro Text", 12))
        breadcrumb_label.setStyleSheet("color: #7f8c8d;")
        header_layout.addWidget(breadcrumb_label)
        
        header_layout.addStretch()
        
        # Action buttons
        new_project_btn = QPushButton("+ New Project")
        new_project_btn.setFont(QFont("SF Pro Text", 12))
        new_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        new_project_btn.clicked.connect(self.new_project)
        header_layout.addWidget(new_project_btn)
        
        import_btn = QPushButton("📁 Import Data")
        import_btn.setFont(QFont("SF Pro Text", 12))
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
        """)
        import_btn.clicked.connect(self.import_data)
        header_layout.addWidget(import_btn)
        
        content_layout.addWidget(header_frame)
        
        # Main content tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e1e5e9;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
        """)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_projects_tab()
        self.create_workflows_tab()
        self.create_analytics_tab()
        
        content_layout.addWidget(self.tab_widget)
        
        # Add to main layout
        main_layout = self.layout()
        main_layout.addWidget(content_frame, 1)  # 1 = stretch factor
    
    def create_right_panel(self):
        """Create the right panel for details and properties"""
        right_panel = ModernFrame()
        right_panel.setMaximumWidth(300)
        right_panel.setMinimumWidth(250)
        
        panel_layout = QVBoxLayout(right_panel)
        panel_layout.setContentsMargins(15, 20, 15, 20)
        panel_layout.setSpacing(15)
        
        # Panel title
        panel_title = QLabel("Properties")
        panel_title.setFont(QFont("SF Pro Display", 14, QFont.Bold))
        panel_title.setStyleSheet("color: #2c3e50;")
        panel_layout.addWidget(panel_title)
        
        # Properties content
        properties_group = QGroupBox("File Info")
        properties_group.setFont(QFont("SF Pro Text", 12))
        properties_layout = QFormLayout(properties_group)
        
        # Sample properties
        properties_layout.addRow("Name:", QLabel("No file selected"))
        properties_layout.addRow("Size:", QLabel("0 KB"))
        properties_layout.addRow("Type:", QLabel("Unknown"))
        properties_layout.addRow("Modified:", QLabel("Never"))
        
        panel_layout.addWidget(properties_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_group.setFont(QFont("SF Pro Text", 12))
        actions_layout = QVBoxLayout(actions_group)
        
        quick_btn = QPushButton("🔍 Analyze Data")
        quick_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        actions_layout.addWidget(quick_btn)
        
        panel_layout.addWidget(actions_group)
        panel_layout.addStretch()
        
        # Add to main layout
        main_layout = self.layout()
        main_layout.addWidget(right_panel)
    
    def create_dashboard_tab(self):
        """Create the dashboard tab with overview content"""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Welcome section
        welcome_frame = ModernFrame()
        welcome_layout = QVBoxLayout(welcome_frame)
        
        welcome_title = QLabel("Welcome to Unified Data Studio")
        welcome_title.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        welcome_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        welcome_layout.addWidget(welcome_title)
        
        welcome_text = QLabel("Your comprehensive platform for data analysis, workflow automation, and business intelligence.")
        welcome_text.setFont(QFont("SF Pro Text", 14))
        welcome_text.setStyleSheet("color: #7f8c8d; line-height: 1.5;")
        welcome_text.setWordWrap(True)
        welcome_layout.addWidget(welcome_text)
        
        layout.addWidget(welcome_frame)
        
        # Stats grid
        stats_frame = ModernFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)
        
        # Create stat cards
        stats = [
            ("📊", "Total Projects", "12", "#007bff"),
            ("🔧", "Active Workflows", "8", "#28a745"),
            ("📁", "Data Files", "156", "#ffc107"),
            ("📈", "Analytics", "24", "#dc3545")
        ]
        
        for i, (icon, title, value, color) in enumerate(stats):
            stat_card = self.create_stat_card(icon, title, value, color)
            stats_layout.addWidget(stat_card, i // 2, i % 2)
        
        layout.addWidget(stats_frame)
        
        # Recent activity
        activity_frame = ModernFrame()
        activity_layout = QVBoxLayout(activity_frame)
        
        activity_title = QLabel("Recent Activity")
        activity_title.setFont(QFont("SF Pro Display", 16, QFont.Bold))
        activity_title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        activity_layout.addWidget(activity_title)
        
        # Activity list
        activities = [
            "📁 Imported sales_data.csv",
            "🔧 Workflow 'Data Cleanup' completed",
            "📊 Created 'Q4 Sales Report' dashboard",
            "⚙️ Updated project settings"
        ]
        
        for activity in activities:
            activity_label = QLabel(activity)
            activity_label.setFont(QFont("SF Pro Text", 12))
            activity_label.setStyleSheet("color: #5a6c7d; padding: 8px 0; border-bottom: 1px solid #f1f3f4;")
            activity_layout.addWidget(activity_label)
        
        layout.addWidget(activity_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(dashboard, "🏠 Dashboard")
    
    def create_stat_card(self, icon, title, value, color):
        """Create a statistics card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}15;
                border: 1px solid {color}30;
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Icon and value
        top_row = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("SF Pro Display", 24))
        top_row.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("SF Pro Display", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        top_row.addWidget(value_label)
        top_row.addStretch()
        
        layout.addLayout(top_row)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("SF Pro Text", 12))
        title_label.setStyleSheet("color: #5a6c7d;")
        layout.addWidget(title_label)
        
        return card
    
    def create_projects_tab(self):
        """Create the projects tab"""
        projects = DataStudioTab("Projects")
        self.tab_widget.addTab(projects, "📁 Projects")
    
    def create_workflows_tab(self):
        """Create the workflows tab"""
        workflows = DataStudioTab("Workflows")
        self.tab_widget.addTab(workflows, "🔧 Workflows")
    
    def create_analytics_tab(self):
        """Create the analytics tab"""
        analytics = DataStudioTab("Analytics")
        self.tab_widget.addTab(analytics, "📊 Analytics")
    
    def navigate_to(self, section):
        """Navigate to a specific section"""
        # Switch to appropriate tab
        if section == "dashboard":
            self.tab_widget.setCurrentIndex(0)
        elif section == "projects":
            self.tab_widget.setCurrentIndex(1)
        elif section == "workflows":
            self.tab_widget.setCurrentIndex(2)
        elif section == "analytics":
            self.tab_widget.setCurrentIndex(3)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def setup_status_updates(self):
        """Setup status update timer"""
        pass
    
    def apply_styling(self):
        """Apply application-wide styling"""
        self.setStyleSheet("""
            QWidget {
                font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif;
            }
        """)
    
    # Action methods
    def new_project(self):
        """Create a new project"""
        QMessageBox.information(self, "New Project", "New project functionality coming soon!")
    
    def import_data(self):
        """Import data files"""
        QMessageBox.information(self, "Import Data", "Data import functionality coming soon!")
