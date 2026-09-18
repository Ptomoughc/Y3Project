import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt

class Error(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Frameless dialog
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 150)  
        self.setWindowModality(Qt.ApplicationModal)

        # Overlay parent
        if parent:
            self.overlay = QWidget(parent)
            self.overlay.setGeometry(parent.rect())
            self.overlay.setStyleSheet("background-color: rgba(0,0,0,80);")
            self.overlay.show()

        self.init_ui()
        self.center_on_parent()

    def init_ui(self):
        # Outer frame with purple border
        self.background_frame = QFrame(self)
        self.background_frame.setGeometry(0, 0, 400, 120)
        self.background_frame.setStyleSheet("""
            background-color: #2a2a2a;
            border-radius: 10px;
        """)

        # Label
        self.label = QLabel("Two conflicting actions detected", self.background_frame)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 16px;")

        # Confirm button 
        self.confirm_button = QPushButton("Confirm", self.background_frame)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #6A0DAD;
                color: white;
                font-size: 14px;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8A2BE2;
            }
        """)
        self.confirm_button.clicked.connect(self.close_window)

        # Layout with evenly spaced elements
        layout = QVBoxLayout(self.background_frame)
        layout.setContentsMargins(20, 15, 20, 15) 
        layout.setSpacing(10)

        # Even vertical spacing
        layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.confirm_button, alignment=Qt.AlignCenter)
        layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.background_frame.setLayout(layout)

    def center_on_parent(self):
        if self.parent:
            parent_geometry = self.parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
        else:
            screen_geometry = QApplication.desktop().screenGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def close_window(self):
        self.close_overlay()
        self.close()

    def close_overlay(self):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.close()
            self.overlay = None

    def closeEvent(self, event):
        self.close_overlay()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = QWidget()
    main_window.setWindowTitle("Main Window")
    main_window.setGeometry(500, 200, 800, 600)
    main_window.show()

    error_dialog = Error(parent=main_window)
    error_dialog.show()

    sys.exit(app.exec_())