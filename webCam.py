import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QCheckBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QIcon, QPixmap

from ML_Folder.gesture_ml import GestureRecognizer

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")


class WebcamWindow(QWidget):
    def __init__(self, main_page, settings_page):
        super().__init__()
        self.setWindowTitle("Add Music Files")
        pixmap = QPixmap("images/H.png").scaled(
            16, 16,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.setWindowIcon(QIcon(pixmap))
        # 1367 to have it to the right of the main page
        self.move(100, 70)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Webcam display
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        main_layout.addWidget(self.image_label)

        # Floating Toggle Checkbox
        self.toggle_checkbox = QCheckBox("Show Hand Lines", self)
        self.toggle_checkbox.setChecked(True)
        self.toggle_checkbox.setMinimumWidth(140)
        self.toggle_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 14px;
                background-color: rgba(30, 30, 30, 180);
                padding: 8px 8px;
                border-radius: 8px;
            }
        """)
        self.toggle_checkbox.move(10, 10)
        self.toggle_checkbox.raise_()

        # Camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("No webcam detected - using dummy frames.")
            self.cap = None  # mark for fallback

        # Gesture system
        self.settings_page = settings_page
        self.mappings = self.settings_page.get_gesture_mappings()
        self.gesture_recognizer = GestureRecognizer(main_page, self.mappings)

        # Live updates from settings
        self.settings_page.settings_saved.connect(self.update_mappings)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    # Keep checkbox positioned on resize
    def resizeEvent(self, event):
        self.toggle_checkbox.move(15, self.height() - 45)
        super().resizeEvent(event)

    # Update mappings dynamically
    def update_mappings(self, new_mappings):
        self.gesture_recognizer.update_gesture_mappings(new_mappings)

    # Frame update
    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if not ret:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

        frame = cv2.flip(frame, 1)

        # Toggle state
        show_lines = self.toggle_checkbox.isChecked()

        processed_frame, _ = self.gesture_recognizer.process_frame(
            frame, draw_landmarks=show_lines
        )

        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

        h, w, ch = processed_frame.shape
        qt_image = QImage(processed_frame.data, w, h, ch * w, QImage.Format_RGB888)

        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    # Cleanup
    def closeEvent(self, event):
        if self.timer.isActive():
            self.timer.stop()

        if self.cap and self.cap.isOpened():
            self.cap.release()

        event.accept()