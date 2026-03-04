from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame
)
from PyQt5.QtGui import QPixmap, QTransform, QIcon
from PyQt5.QtCore import Qt, QSize


class TutorialPage1(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Top bar (Back button + Title)
        top_bar = QHBoxLayout()

        pixmap = QPixmap("images/backButton")
        rotated = pixmap.transformed(
            QTransform().rotate(180),
            Qt.SmoothTransformation
        )

        back_button = QPushButton()
        back_button.setIcon(QIcon("images/backButton"))
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

        title_label = QLabel("Tutorial")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: white;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)

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

        top_bar.addWidget(back_button, alignment=Qt.AlignLeft)
        top_bar.addStretch()
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(next_button, alignment=Qt.AlignRight)

        main_layout.addLayout(top_bar)

        # Bordered grid container
        border_frame = QFrame()
        border_frame.setStyleSheet("""
            QFrame {
                border: 3px solid white;
                border-radius: 15px;
            }
        """)

        grid_layout = QGridLayout(border_frame)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setSpacing(20)

        # 2x3 image slots
        self.image_slots = []

        for row in range(2):
            for col in range(3):
                slot = QLabel("Image\nPlaceholder")
                slot.setAlignment(Qt.AlignCenter)
                slot.setStyleSheet("""
                    QLabel {
                        border: 2px dashed white;
                        color: white;
                        font-size: 14px;
                    }
                """)
                slot.setMinimumSize(100, 100)
                slot.setSizePolicy(
                    slot.sizePolicy().Expanding,
                    slot.sizePolicy().Expanding
                )

                grid_layout.addWidget(slot, row, col)
                self.image_slots.append(slot)

        # Make grid stretch evenly
        for i in range(3):
            grid_layout.setColumnStretch(i, 1)
        for i in range(2):
            grid_layout.setRowStretch(i, 1)

        main_layout.addWidget(border_frame, stretch=1)

    def go_back(self):
        self.controller.setCurrentIndex(0)
    
    def go_forwards(self):
        self.controller.setCurrentIndex(2)
