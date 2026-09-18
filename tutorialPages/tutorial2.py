import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QGridLayout, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QTransform, QIcon
from PyQt5.QtCore import Qt, QSize


class TutorialPage2(QWidget):
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

        title_label = QLabel("Customising Gestures")
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

        top_bar.addWidget(back_button)
        top_bar.addStretch()
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(next_button)
        main_layout.addLayout(top_bar)

        # Grid container
        border_frame = QFrame()
        border_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        border_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        grid_layout = QGridLayout(border_frame)
        grid_layout.setContentsMargins(25, 25, 25, 25)
        grid_layout.setSpacing(25)

        # Data
        self.images = ["images/b3.jpg", "images/c2.png", "images/c3.png", "images/c4.png", "images/c5.png", "images/c6.png"]
        self.captions = ["Click the settiings icon", "Open settings page", "Choose the function you would like to edit", "Choose the gesture you would like to map", "Press save to save changes - ensure all mappings are always unique", "Press revert to return to default mappings"]
        self.image_slots = []

        # 2x3 Grid
        for row in range(2):
            for col in range(3):
                index = row * 3 + col

                # Card container
                card = QFrame()
                card.setStyleSheet("""
                    QFrame {
                        background-color: rgba(255, 255, 255, 0.08);
                        border-radius: 12px;
                    }
                    QFrame:hover {
                        background-color: rgba(255, 255, 255, 0.12);
                    }
                """)
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(20, 20, 20, 20)
                card_layout.setSpacing(12)

                # Image
                image_label = QLabel()
                image_label.setAlignment(Qt.AlignCenter)
                image_label.setMinimumSize(280, 180)
                image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                image_label.setStyleSheet("""
                    QLabel {
                        border-radius: 8px;
                        background-color: #1e1e1e;
                    }
                """)

                pixmap = QPixmap(self.images[index])
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        image_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    image_label.setPixmap(scaled_pixmap)

                    # Resize handler to keep image scaled
                    def create_resize_handler(label, original_pixmap):
                        def resize_event(event):
                            if not original_pixmap.isNull():
                                scaled = original_pixmap.scaled(
                                    label.size(),
                                    Qt.KeepAspectRatio,
                                    Qt.SmoothTransformation
                                )
                                label.setPixmap(scaled)
                            QLabel.resizeEvent(label, event)
                        return resize_event

                    image_label.original_pixmap = pixmap
                    image_label.resizeEvent = create_resize_handler(image_label, pixmap)

                # Caption - vertically centered
                caption_label = QLabel(self.captions[index])
                caption_label.setAlignment(Qt.AlignCenter)
                caption_label.setWordWrap(True)
                caption_label.setMinimumHeight(35)
                caption_label.setMaximumHeight(50)
                caption_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
                caption_label.setStyleSheet("""
                    QLabel {
                        color: white;
                        font-size: 13px;
                        border-top: 1px solid rgba(255, 255, 255, 0.3);
                        padding-top: 8px;
                        padding-bottom: 8px;
                    }
                """)

                # Vertical layout wrapper to center caption
                caption_wrapper = QVBoxLayout()
                caption_wrapper.addWidget(caption_label)
                caption_wrapper.setContentsMargins(0, 0, 0, 0)
                caption_wrapper.setAlignment(Qt.AlignVCenter)

                # Add image and caption to card
                card_layout.addWidget(image_label, stretch=1)
                card_layout.addLayout(caption_wrapper)

                # Add card to grid
                grid_layout.addWidget(card, row, col)
                grid_layout.setRowStretch(row, 1)
                grid_layout.setColumnStretch(col, 1)

                # Store references
                self.image_slots.append((image_label, caption_label))

        # Stretch rows and columns equally
        for i in range(3):
            grid_layout.setColumnStretch(i, 1)
        for i in range(2):
            grid_layout.setRowStretch(i, 1)

        main_layout.addWidget(border_frame, stretch=1)

    # Navigation
    def go_back(self):
        self.controller.setCurrentIndex(1)

    def go_forwards(self):
        self.controller.setCurrentIndex(3)