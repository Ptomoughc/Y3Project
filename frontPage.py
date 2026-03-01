from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
import sys
import subprocess

class FrontPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(40)
        main_layout.setContentsMargins(60, 80, 60, 80)
        self.setLayout(main_layout)

        # Title Section
        title_label = QLabel("Jesture Player")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: white;
                padding: 25px 40px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                           stop: 0 #8B5FBF, stop: 0.3 #6A0DAD, stop: 0.7 #6A0DAD, stop: 1 #8B5FBF);
                border-radius: 20px;
                border: 2px solid #9D4EDD;
                margin-bottom: 10px;
            }
        """)

        subtitle_label = QLabel("Gesture-Controlled Media Player")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #b8b8b8;
                padding: 10px;
                font-weight: normal;
                margin-bottom: 40px;
            }
        """)

        # Play Button Section
        play_button = QPushButton("▶")
        play_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 60px;
                font-weight: bold;
                border: 3px solid #9D4EDD;
                border-radius: 55px;
                padding: 0px;
                min-width: 110px;
                min-height: 110px;
            }
            QPushButton:hover {
                background-color: rgba(157, 78, 221, 0.2);
                border: 3px solid #BA8AFF;
                color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: rgba(106, 13, 173, 0.3);
                border: 3px solid #9D4EDD;
                color: #E0E0E0;
            }
        """)
        play_button.setFixedSize(110, 110)
        play_button.setContentsMargins(10, 0, 0, 0)

        play_label = QLabel("Start Playing")
        play_label.setAlignment(Qt.AlignCenter)
        play_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #b8b8b8;
                font-weight: medium;
                padding: 5px;
                margin-top: 15px;
            }
        """)

        # Tutorial Button Section
        tutorial_button = QPushButton("TUTORIAL")
        tutorial_button.setFixedSize(220, 65)
        tutorial_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                 stop: 0 #5A0A9A, stop: 1 #4A0D8B);
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #7B3FA3;
                border-radius: 12px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                 stop: 0 #6A0DAD, stop: 1 #5A0A9A);
                border: 2px solid #9D4EDD;
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                 stop: 0 #4A0DAD, stop: 1 #3A0A6B);
            }
        """)

        # Footer Section
        footer_label = QLabel("Control your media with intuitive hand gestures")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #888;
                font-style: italic;
                padding: 10px;
                margin-top: 20px;
            }
        """)

        # Add widgets to main layout
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)
        main_layout.addWidget(play_button, alignment=Qt.AlignCenter)
        main_layout.addWidget(play_label, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)
        main_layout.addWidget(tutorial_button, alignment=Qt.AlignCenter)
        main_layout.addWidget(footer_label, alignment=Qt.AlignCenter)

        # Connect signals
        play_button.clicked.connect(self.open_main_page)
        tutorial_button.clicked.connect(self.open_tutorial_page)

    def open_main_page(self):
        # Switch to main player page using controller
        self.controller.setCurrentIndex(3)

    def open_tutorial_page(self):
        # Switch to tutorial page using controller
        self.controller.setCurrentIndex(1)