from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QGridLayout, QComboBox, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QSize
import sys


def white_placeholder_icon(size=32):
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("white"))
    return QIcon(pixmap)


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Settings")
window.resize(600, 700)

main_layout = QVBoxLayout(window)
main_layout.setContentsMargins(20, 20, 20, 20)

grid = QGridLayout()
grid.setSpacing(20)

functions = ["Play", "Pause", "Skip", "Rewind", "Loop", "Shuffle"]

GESTURES = [
    "Fist",
    "Open Hand",
    "Thumb Left",
    "Thumb Right",
    "Pinky Left",
    "Pinky Right",
]

# 🔹 Preset mappings
PRESETS = {
    "Play": "Fist",
    "Pause": "Open Hand",
    "Skip": "Thumb Right",
    "Rewind": "Thumb Left",
    "Loop": "Pinky Left",
    "Shuffle": "Pinky Right",
}

# Store combo boxes so we can access them later
combo_boxes = {}

def create_mapping_cell(title_text):
    container = QWidget()
    container.setStyleSheet("""
        QWidget {
            background-color: #333333;
            border: 1px solid #444444;
            border-radius: 10px;
        }
    """)

    layout = QVBoxLayout(container)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(10)

    title = QLabel(title_text)
    title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
    title.setAlignment(Qt.AlignCenter)

    combo = QComboBox()
    combo.setIconSize(QSize(32, 32))
    combo.setStyleSheet("""
        QComboBox {
            background-color: #f8f8f8;
            padding: 6px;
            border-radius: 6px;
            font-size: 13px;
        }
        QComboBox QAbstractItemView {
            padding: 5px;
        }
    """)

    placeholder_icon = white_placeholder_icon(32)

    for gesture in GESTURES:
        combo.addItem(placeholder_icon, gesture)

    # 🔹 Set preset as default
    if title_text in PRESETS:
        index = combo.findText(PRESETS[title_text])
        if index >= 0:
            combo.setCurrentIndex(index)

    layout.addWidget(title)
    layout.addWidget(combo)

    combo_boxes[title_text] = combo

    return container


# Add 3x2 grid
row = 0
col = 0
for func in functions:
    grid.addWidget(create_mapping_cell(func), row, col)
    col += 1
    if col > 1:
        col = 0
        row += 1

main_layout.addLayout(grid)


# 🔹 SAVE FUNCTION
def save_settings():
    print("Saved Settings:")
    for func, combo in combo_boxes.items():
        print(f"{func} → {combo.currentText()}")


# 🔹 REVERT FUNCTION
def revert_settings():
    for func, combo in combo_boxes.items():
        preset = PRESETS.get(func)
        if preset:
            index = combo.findText(preset)
            if index >= 0:
                combo.setCurrentIndex(index)


# Buttons Layout
button_layout = QHBoxLayout()

save_button = QPushButton("Save")
revert_button = QPushButton("Revert")

save_button.clicked.connect(save_settings)
revert_button.clicked.connect(revert_settings)

button_layout.addWidget(save_button)
button_layout.addWidget(revert_button)

main_layout.addLayout(button_layout)

window.show()
sys.exit(app.exec_())
