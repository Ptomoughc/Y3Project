import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap

# Import the ML module
from ML_Folder.gesture_ml import GestureRecognizer
from settings import SettingsPage

class WebcamWindow(QWidget):
    def __init__(self, main_page):
        super().__init__()
        self.setGeometry(1367, 100, 800, 600)

        self.setWindowTitle("PyQt5 Webcam")
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(800, 600)
        self.image_label.setScaledContents(True)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # OpenCV video capture
        self.cap = cv2.VideoCapture(0)

        # Create gesture recognizer instance
        self.settings_page = SettingsPage()
        self.mappings = self.settings_page.get_gesture_mappings()
        self.gesture_recognizer = GestureRecognizer(main_page, self.mappings)

        # Timer to grab frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 FPS

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
    
        frame = cv2.flip(frame, 1)

        # Send frame to ML processor
        processed_frame, gesture = self.gesture_recognizer.process_frame(frame)

        # Convert BGR to RGB for display
        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

        h, w, ch = processed_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(processed_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):

        if self.timer.isActive():
            self.timer.stop()

        if self.cap.isOpened():
            self.cap.release()

        event.accept()
