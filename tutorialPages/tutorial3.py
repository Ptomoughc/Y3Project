import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QTransform, QIcon
from PyQt5.QtCore import Qt, QSize


class TutorialPage3(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Top bar
        top_bar = QHBoxLayout()

        pixmap = QPixmap("images/backButton.png")
        rotated = pixmap.transformed(
            QTransform().rotate(180),
            Qt.SmoothTransformation
        )

        back_button = QPushButton()
        back_button.setIcon(QIcon("images/backButton.png"))
        back_button.setIconSize(QSize(30, 30))
        back_button.setFixedSize(100, 50)
        back_button.clicked.connect(self.go_back)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #6A0DAD;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B5FBF;
            }
        """)

        title_label = QLabel("Ensuring High Accuracy")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: white;
            }
        """)

        next_button = QPushButton()
        next_button.setIcon(QIcon(rotated))
        next_button.setIconSize(QSize(30, 30))
        next_button.setFixedSize(100, 50)
        next_button.clicked.connect(self.go_forwards)
        next_button.setStyleSheet("""
            QPushButton {
                background-color: #6A0DAD;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B5FBF;
            }
        """)

        top_bar.addWidget(back_button)
        top_bar.addStretch()
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(next_button)

        main_layout.addLayout(top_bar)

        # Center container
        outer_frame = QFrame()
        outer_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        outer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(40, 40, 40, 40)
        outer_layout.setSpacing(25)
        outer_layout.setAlignment(Qt.AlignCenter)

        # Inner card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 15px;
            }
        """)
        card.setMaximumWidth(1000)
        card.setMinimumWidth(1000)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(18)

        # Tips list
        tips = [
            "Keep your hand close to the webcam",
            "Face your hand directly towards the camera",
            "Use a clear, uncluttered background",
            "Ensure good, even lighting",
            "Keep your full hand visible in frame",
            "Make sure your whole hand is visible",
            "Keep the camera stable (no shaking)",
            "Keep your hand at a constant distance from the camera"
        ]

        for i, tip in enumerate(tips, start=1):
            label = QLabel(f"{i}. {tip}")
            label.setWordWrap(True)
            label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                    border-radius: 8px;
                }
                QLabel:hover {
                    background-color: rgba(255, 255, 255, 0.08);
                }
            """)
            card_layout.addWidget(label)

        outer_layout.addWidget(card)
        main_layout.addWidget(outer_frame, stretch=1)

    # Navigation
    def go_back(self):
        self.controller.setCurrentIndex(2)

    def go_forwards(self):
        self.controller.setCurrentIndex(4)