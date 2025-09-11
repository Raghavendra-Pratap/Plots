# main.py
import warnings
warnings.filterwarnings("error")
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from pages.home_page import HomePage  # ← import HomePage

class DataStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Studio")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()

    def setup_ui(self):
        self.home_page = HomePage()  # ← create HomePage
        self.setCentralWidget(self.home_page)  # ← set HomePage as main content

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataStudio()
    window.show()
    sys.exit(app.exec_())