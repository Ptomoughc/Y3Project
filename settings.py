from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout,
    QComboBox, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize


# Internal gesture labels (must match ML file exactly)
GESTURES = [
    "fist",
    "open",
    "thumb_left",
    "thumb_right",
    "pinky_left",
    "pinky_right"
]

# Default preset mappings (gesture to action)
PRESETS = {
    "fist": "play",
    "open": "pause",
    "thumb_right": "rewind",
    "thumb_left": "loop",
    "pinky_left": "shuffle",
    "pinky_right": "skip",
}


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(600, 700)

        # Stores gesture to action mappings
        self.current_mappings = PRESETS.copy()
        self.combo_boxes = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        grid = QGridLayout()
        grid.setSpacing(20)

        row = 0
        col = 0
        for gesture in GESTURES:
            grid.addWidget(self.create_mapping_cell(gesture), row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        main_layout.addLayout(grid)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        revert_button = QPushButton("Revert")

        save_button.clicked.connect(self.save_settings)
        revert_button.clicked.connect(self.revert_settings)

        button_layout.addWidget(save_button)
        button_layout.addWidget(revert_button)
        main_layout.addLayout(button_layout)

    def white_placeholder_icon(self, size=32):
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor("white"))
        return QIcon(pixmap)

    def format_label(self, text):
        # Convert internal label to readable display text
        return text.replace("_", " ").title()

    def create_mapping_cell(self, gesture_label):
        container = QWidget()
        container.setStyleSheet(
            "background-color: #333333; border:1px solid #444; border-radius:10px;"
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title (Gesture name)
        title = QLabel(self.format_label(gesture_label))
        title.setStyleSheet(
            "color: white; font-size:16px; font-weight:bold;"
        )
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Action dropdown
        combo = QComboBox()
        combo.setIconSize(QSize(32, 32))
        combo.setStyleSheet(
            "QComboBox { background-color:#f8f8f8; padding:6px; border-radius:6px; font-size:13px; }"
        )

        placeholder_icon = self.white_placeholder_icon()

        actions = ["play", "pause", "skip", "rewind", "loop", "shuffle", "none"]

        for action in actions:
            combo.addItem(placeholder_icon, action)

        # Set preset
        preset_action = PRESETS.get(gesture_label)
        if preset_action:
            index = combo.findText(preset_action)
            if index >= 0:
                combo.setCurrentIndex(index)

        layout.addWidget(combo)

        self.combo_boxes[gesture_label] = combo
        return container

    def save_settings(self):
        # Update gesture → action mappings
        for gesture, combo in self.combo_boxes.items():
            self.current_mappings[gesture] = combo.currentText()

        print("Saved Settings:")
        for gesture, action in self.current_mappings.items():
            print(f"{gesture} -> {action}")

    def revert_settings(self):
        # Revert to default preset mappings
        for gesture, combo in self.combo_boxes.items():
            preset_action = PRESETS.get(gesture)
            if preset_action:
                index = combo.findText(preset_action)
                if index >= 0:
                    combo.setCurrentIndex(index)

        self.current_mappings = PRESETS.copy()
        print("Reverted to presets")

    def get_gesture_mappings(self):
        # Return gesture to action mapping
        return self.current_mappings.copy()