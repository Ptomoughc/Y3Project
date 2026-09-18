import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

class DragDropWindow(QWidget):
    def __init__(self, target_folder, on_files_added=None):
        super().__init__()
        self.target_folder = target_folder
        self.on_files_added = on_files_added  # notify main window
        self.setStyleSheet("background-color: #2a2a2a")

        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)

        self.setWindowTitle("Add Music Files")
        pixmap = QPixmap("images/H.png").scaled(
            16, 16,  
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.setWindowIcon(QIcon(pixmap))
        self.setGeometry(530, 420, 400, 200)
        self.setFixedSize(400, 200)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAcceptDrops(True)

        self.label = QLabel('Drag and drop MP3 files here\n\nName Format: " Title - Artist "', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "border: 2px dashed #6A0DAD; color: white; font-size: 16px; padding: 20px;"
        )

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        added_files = []
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith(".mp3"):
                try:
                    base_name = os.path.basename(file_path)
                    target_path = os.path.join(self.target_folder, base_name)
                    shutil.copy(file_path, target_path)
                    added_files.append(target_path)
                except Exception as e:
                    print(f"Error copying file {file_path}: {e}")

        if added_files:
            print("Added files:", added_files)
            if self.on_files_added:
                self.on_files_added(added_files)  # notify main page

        event.acceptProposedAction()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    songs_folder = r"C:\Users\Thomas\Desktop\Year3 Coursework\songs"

    window = DragDropWindow(songs_folder)
    window.show()

    sys.exit(app.exec_())
