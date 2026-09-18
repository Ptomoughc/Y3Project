from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout,
    QComboBox, QPushButton, QHBoxLayout, QStyle, QStyleOptionComboBox
)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QPolygon
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint

from error import Error

GESTURES = [
    "fist", "open", "thumb_left",
    "thumb_right", "pinky_left", "pinky_right"
]

ACTIONS = ["play", "pause", "skip", "rewind", "loop", "shuffle"]

PRESETS = {
    "fist": "play",
    "open": "pause",
    "thumb_right": "rewind",
    "thumb_left": "loop",
    "pinky_left": "shuffle",
    "pinky_right": "skip",
}

GESTURE_DISPLAY = {
    "fist": "Closed Hand",
    "open": "Open Hand",
    "thumb_left": "Left Thumb",
    "thumb_right": "Right Thumb",
    "pinky_left": "Left Pinky",
    "pinky_right": "Right Pinky"
}


class VArrowComboBox(QComboBox):
    """Custom ComboBox with a V-shaped downward arrow"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def paintEvent(self, event):
        # Call the original paint event first
        super().paintEvent(event)
        
        # Create a painter to draw the custom arrow
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get the drop-down button rectangle
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        arrow_rect = self.style().subControlRect(
            QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow, self
        )
        
        # Draw a V-shaped arrow (downward pointing triangle)
        if self.isEnabled():
            # Calculate the center point of the arrow area
            center_x = arrow_rect.center().x()
            center_y = arrow_rect.center().y()
            
            # Scale up the arrow size proportionally
            arrow_width = 14
            arrow_height = 12
            
            # Create polygon for downward V
            polygon = QPolygon()
            polygon.append(QPoint(center_x - arrow_width//2, center_y - arrow_height//3))
            polygon.append(QPoint(center_x + arrow_width//2, center_y - arrow_height//3))
            polygon.append(QPoint(center_x, center_y + arrow_height//2))
            
            # Set pen and brush for the arrow
            painter.setPen(Qt.NoPen)
            
            # Check if hovered
            if opt.state & QStyle.State_MouseOver:
                painter.setBrush(QColor("#9b30ff"))  # Purple on hover
            else:
                painter.setBrush(QColor("#e0e0e0"))  # Light gray normally
            
            # Draw the triangle
            painter.drawPolygon(polygon)
        
        painter.end()


class SettingsPage(QWidget):
    settings_saved = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        pixmap = QPixmap("images/H.png").scaled(
            16, 16,  
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.setWindowIcon(QIcon(pixmap))
        self.setGeometry(100, 100, 600, 700)

        # Background design
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                           stop: 0 #0d0d0d, stop: 0.5 #121212, stop: 1 #1a1a1a);
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #e0e0e0;
            }
        """)

        self.current_mappings = PRESETS.copy()
        self.combo_boxes = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        grid = QGridLayout()
        grid.setSpacing(20)

        row = 0
        col = 0

        for action in ACTIONS:
            grid.addWidget(self.create_mapping_cell(action), row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        main_layout.addLayout(grid)


        # Buttons
        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        revert_button = QPushButton("Revert")

        button_style = """
            QPushButton {
                background-color: #6a0dad;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7b1fe0;
            }
            QPushButton:pressed {
                background-color: #4b0082;
            }
        """

        save_button.setStyleSheet(button_style)
        revert_button.setStyleSheet(button_style)

        save_button.clicked.connect(self.save_settings)
        revert_button.clicked.connect(self.revert_settings)

        button_layout.addWidget(save_button)
        button_layout.addWidget(revert_button)
        main_layout.addLayout(button_layout)


    # Icon placeholder 
    def white_placeholder_icon(self, size=32):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        from PyQt5.QtGui import QPainter, QPen

        painter = QPainter(pixmap)

        painter.fillRect(1, 1, size - 2, size - 2, QColor("#f0f0f0"))

        pen = QPen(QColor("#666666"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(0, 0, size - 1, size - 1)

        painter.end()

        return QIcon(pixmap)

    def format_label(self, text):
        return text.replace("_", " ").title()


    # Mapping cell
    def create_mapping_cell(self, action_label):
        container = QWidget()
        container.setStyleSheet(
            "background-color: #333333; border:1px solid #444; border-radius:10px;"
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel(self.format_label(action_label))
        title.setStyleSheet(
            "color: white; font-size:16px; font-weight:bold;"
        )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        combo = VArrowComboBox()
        combo.setIconSize(QSize(40, 40))

        combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                padding: 8px;
                padding-right: 40px;
                border-radius: 8px;
                font-size: 13px;
                border: 2px solid #555;
                min-height: 24px;
            }
            QComboBox:hover {
                border: 2px solid #9b30ff;
                background-color: #3a3a3a;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 36px;
                border-left: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: white;
                selection-background-color: #6a0dad;
                border: 2px solid #9b30ff;
                padding: 4px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                min-height: 28px;
            }
        """)

        # Map gestures to correct image files
        icon_map = {
            "fist": "images/F.png",
            "open": "images/H.png",
            "thumb_left": "images/T.png",
            "thumb_right": "images/T2.png",
            "pinky_left": "images/P.png",
            "pinky_right": "images/P2.png",
        }

        # Add items with icons
        for gesture in GESTURES:
            icon_path = icon_map.get(gesture, "")
            icon = QIcon(icon_path) if icon_path else QIcon()
            combo.addItem(icon, GESTURE_DISPLAY[gesture], gesture)

        # preset selection
        for gesture, action in PRESETS.items():
            if action == action_label:
                index = combo.findData(gesture)
                if index >= 0:
                    combo.setCurrentIndex(index)
                break

        layout.addWidget(combo)

        self.combo_boxes[action_label] = combo
        return container

    # Save
    def save_settings(self):
        new_mappings = {}
        selected_gestures = []

        for action, combo in self.combo_boxes.items():
            gesture = combo.currentData()
            selected_gestures.append(gesture)
            new_mappings[gesture] = action

        if len(set(selected_gestures)) != len(GESTURES):
            self.show_conflict_error()
            return

        self.current_mappings = new_mappings

        print("Saved Settings:")
        for gesture, action in self.current_mappings.items():
            print(f"{gesture} -> {action}")

        # Send to webcam/ML
        self.settings_saved.emit(new_mappings)

    def show_conflict_error(self):
        error_dialog = Error(parent=self)
        error_dialog.show()

    # Revert
    def revert_settings(self):
        for action, combo in self.combo_boxes.items():
            for gesture, preset_action in PRESETS.items():
                if preset_action == action:
                    index = combo.findData(gesture)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                    break

        self.current_mappings = PRESETS.copy()
        print("Reverted to presets")

    def get_gesture_mappings(self):
        return self.current_mappings.copy()