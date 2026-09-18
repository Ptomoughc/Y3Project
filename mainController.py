from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QIcon, QPixmap
import sys
from frontPage import FrontPage
from tutorialPages.tutorial1 import TutorialPage1
from tutorialPages.tutorial2 import TutorialPage2
from tutorialPages.tutorial3 import TutorialPage3
from tutorialPages.tutorial4 import TutorialPage4
from main import MainPlayerPage
from PyQt5.QtCore import Qt

class MainController(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setGeometry(100, 100, 1260, 840)
        self.setWindowTitle("Jesture Player")
        pixmap = QPixmap("images/H.png").scaled(
            16, 16,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.setWindowIcon(QIcon(pixmap))
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #0d0d0d, stop: 0.5 #121212, stop: 1 #1a1a1a);
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #e0e0e0;
            }
        """)
        
        # Create pages and pass reference to controller
        self.front_page = FrontPage(self)
        self.tutorial_page1 = TutorialPage1(self)
        self.tutorial_page2 = TutorialPage2(self)
        self.tutorial_page3 = TutorialPage3(self)
        self.tutorial_page4 = TutorialPage4(self)
        self.main_player_page = MainPlayerPage(self)
        
        # Add pages to stacked widget
        self.addWidget(self.front_page)
        self.addWidget(self.tutorial_page1)
        self.addWidget(self.tutorial_page2)
        self.addWidget(self.tutorial_page3)
        self.addWidget(self.tutorial_page4)
        self.addWidget(self.main_player_page)

    def closeEvent(self, event):
        # Override close event to close settings page when main window closes
        if hasattr(self.main_player_page, 'close_settings_page'):
            self.main_player_page.close_settings_page()
            self.main_player_page.close_webcam_page()
        
        # Accept the close event
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = MainController()
    controller.show()
    sys.exit(app.exec())