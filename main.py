import warnings
import os
import sys
import subprocess
import time
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QStyle, QStyleOptionSlider

# Suppress warnings and pygame startup message
warnings.filterwarnings("ignore", category=UserWarning, module="pkgdata")
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from PyQt5.QtWidgets import QWidget, QPushButton, QSlider, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QLineEdit, QScrollArea, QApplication
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
from PIL import Image
from songs.musicController import music_player
from dragNDrop import DragDropWindow
from ML_Folder.gesture_ml import GestureRecognizer
from settings import SettingsPage
from webCam import WebcamWindow
import sys
import subprocess
import os

class ClickableSlider(QSlider): 
    clicked = pyqtSignal(int) 
    def mousePressEvent(self, event: QMouseEvent): 
        if event.button() == Qt.LeftButton: 
            val = self.minimum() + ((self.maximum() - self.minimum()) * event.x()) // self.width() 
            self.setValue(val) 
            event.accept() 
        super().mousePressEvent(event)

class MainPlayerPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.settings_page = None
        self.webcam_process = None
        self.drag_drop_window = None
        self.songs_folder = r"C:\Users\Thomas\Desktop\Year3 Coursework\songs"
        self.muted = 0
        self.saved_volume = 0
        self.is_playing = False
        self.current_position = 0
        self.total_duration = 225
        self.was_paused = False
        self.pause_position = 0 
        self.last_rewind_click = 0.0
        self.REWIND_DOUBLE_CLICK_THRESHOLD = 1.0
        self.loop_check = False
        self.shuffle_check = False
        
        # Initialize music controller
        self.music_player = music_player
        
        self.setup_ui()
        self.setup_connections()
        
        # Load and display playlist
        self.load_playlist()

        # Load the first song
        self.load_first_song_paused()

        # Initialize gesture recognizer with correct mapping function
        self.settings_page = SettingsPage()
        self.mappings = self.settings_page.get_gesture_mappings()
        self.gesture_recognizer = GestureRecognizer(self, self.mappings)
        self.webcamWindow = None
    
    def is_process_running(self, process):
        return process is not None and process.poll() is None   
        
    def load_playlist(self):
        # Load and display the playlist in the library
        playlist = self.music_player.get_playlist()
        self.update_playlist_ui(playlist)

        if playlist:
            self.update_song_display()

    def setup_ui(self):
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Top Bar Container
        self.back = QPushButton()
        self.settings = QPushButton()
        self.folder = QPushButton()
        self.hand = QPushButton()
        self.title = QLabel("Jesture Player")

        self.settings.setIcon(QIcon("images/settingsIcon"))
        self.back.setIcon(QIcon("images/home"))
        self.folder.setIcon(QIcon("images/folder"))
        self.hand.setIcon(QIcon("images/hand"))

        # Create top container layout
        top_container = QHBoxLayout()
        top_container.setContentsMargins(10, 5, 10, 5)

        # Add widgets to top container
        top_container.addWidget(self.back)
        top_container.addWidget(self.title, 1)
        top_container.addWidget(self.folder)
        top_container.addWidget(self.hand)
        top_container.addWidget(self.settings)

        # Add top container to main layout
        main_layout.addLayout(top_container)

        # Add separator line - PURPLE
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #6A0DAD;")
        main_layout.addWidget(line)

        # Create horizontal layout for main content
        main_content_layout = QHBoxLayout()
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(0)

        # Left Bar Container
        left_widget = QWidget()
        left_widget.setFixedWidth(360)
        left_container = QVBoxLayout(left_widget)
        left_container.setContentsMargins(10, 10, 10, 10)
        left_container.setSpacing(10)

        # Add widgets to Left container
        Library = QLabel("Library")
        Library.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background-color: transparent;")
        
        self.search_library = QLineEdit()
        self.search_library.setPlaceholderText("Search library...")
        self.search_library.setFixedWidth(200)
        self.search_library.setStyleSheet("""
            QLineEdit {
                background-color: #f8f8f8;
                border: 1px solid #6A0DAD;
                border-radius: 5px;
                padding: 5px;
                color: black;
            }
        """)
        
        left_container.addWidget(Library)
        left_container.addWidget(self.search_library)

        # Create scroll area for the library content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #6A0DAD;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a2a;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #6A0DAD;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8B5FBF;
            }
        """)

        # Create content widget for scroll area
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Songs section
        songs_label = QLabel("Songs")
        songs_label.setStyleSheet("font-weight: bold; color: white; margin-top: 10px; font-size: 14px; background-color: transparent;")
        self.scroll_layout.addWidget(songs_label)

        self.playlist_spacer = QSpacerItem(
            1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.scroll_layout.addItem(self.playlist_spacer)

        scroll_area.setWidget(scroll_content)
        left_container.addWidget(scroll_area)
        main_content_layout.addWidget(left_widget)

        # Add vertical separator line - PURPLE
        left_line = QFrame()
        left_line.setFrameShape(QFrame.VLine)
        left_line.setFrameShadow(QFrame.Sunken)
        left_line.setStyleSheet("background-color: #6A0DAD;")
        main_content_layout.addWidget(left_line)

        # Create content area for the rest of the widgets
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        main_content_layout.addWidget(content_widget, 1)

        # Add the main content layout to the main layout
        main_layout.addLayout(main_content_layout, 1)

        # Add horizontal separator line before bottom bar - PURPLE
        bottom_separator = QFrame()
        bottom_separator.setFrameShape(QFrame.HLine)
        bottom_separator.setFrameShadow(QFrame.Sunken)
        bottom_separator.setStyleSheet("background-color: #6A0DAD;")
        main_layout.addWidget(bottom_separator)

        # Bottom Bar Widgets
        self.status = QLabel("Ready")
        self.status.setStyleSheet("color: white; background-color: transparent;")
        
        self.track_count = QLabel("0 Tracks")
        self.track_count.setStyleSheet("color: white; background-color: transparent;")

        # Bottom Bar Container
        bottom_widget = QWidget()
        bottom_widget.setFixedHeight(40)
        bottom_widget.setStyleSheet("background-color: transparent;")
        bottom_container = QHBoxLayout(bottom_widget)
        bottom_container.setContentsMargins(10, 5, 10, 5)
        bottom_container.setSpacing(10)

        bottom_container.addWidget(self.status)
        bottom_container.addWidget(self.track_count, alignment=Qt.AlignRight)
        main_layout.addWidget(bottom_widget)

        # Set button sizes and positions
        self.title.setContentsMargins(20, 0, 0, 0)
        self.title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background-color: transparent;")
        
        # Style the buttons at the top bar
        top_buttons_style = """
            QPushButton {
                background-color: transparent; 
                color: #666;
                border: none;
            }
            QPushButton:hover {
                color: #000;
                cursor: pointer;
            }
        """

        self.back.setFixedSize(50, 50)
        self.back.setIconSize(QSize(30, 30))
        self.back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back.setStyleSheet(top_buttons_style)
        
        self.settings.setFixedSize(50, 50)
        self.settings.setIconSize(QSize(30, 30))
        self.settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings.setStyleSheet(top_buttons_style)
        
        self.folder.setFixedSize(50, 50)
        self.folder.setIconSize(QSize(30, 30))
        self.folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.folder.setStyleSheet(top_buttons_style)
        
        self.hand.setFixedSize(50, 50)
        self.hand.setIconSize(QSize(30, 30))
        self.hand.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hand.setStyleSheet(top_buttons_style)

        # Apply layout to content widget
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 20, 0, 0)
        content_layout.setSpacing(20)

        # Media Image
        self.mediaImage = QPushButton()
        self.mediaImage.setIcon(QIcon("images/glasses.jpg"))
        self.mediaImage.setFixedSize(412, 412)
        self.mediaImage.setIconSize(QSize(300, 300))
        self.mediaImage.setStyleSheet("background-color: transparent; border: none;")

        # Media Title and Artist 
        self.mediaTitle = QLabel("Song Name")
        self.mediaTitle.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background-color: transparent;")
        
        self.mediaArtist = QLabel("Artist")
        self.mediaArtist.setStyleSheet("color: white; font-size: 18px; background-color: transparent;")

        # Get image dimensions
        try:
            with Image.open("images/glasses.jpg") as img:
                width, height = img.size
                if width <= height:
                    size = int((412/width)*width)
                else:
                    size = int((412/height)*width)
                self.mediaImage.setIconSize(QSize(size, size))
        except Exception as e:
            print(f"Error loading image: {e}")

        # Add image to content layout
        content_layout.addWidget(self.mediaImage, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.mediaTitle, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.mediaArtist, alignment=Qt.AlignCenter)

        # Middle container for all controls with border
        middle_container_widget = QWidget()
        middle_container_widget.setObjectName("middleContainer")
        middle_container_widget.setFixedHeight(200)
        middle_container_widget.setStyleSheet("""
            QWidget#middleContainer {
                border: 2px solid #6A0DAD;
                border-radius: 10px;
                background-color: #2a2a2a;
                margin: 10px 20px;
            }
        """)

        middle_container = QVBoxLayout(middle_container_widget)
        middle_container.setContentsMargins(20, 15, 20, 15)
        middle_container.setSpacing(15)
        middle_container.setAlignment(Qt.AlignCenter)

        # Progress bar section
        progress_section = QHBoxLayout()
        progress_section.setSpacing(10)
        progress_section.setAlignment(Qt.AlignCenter)

        self.current_time = QLabel("0:00")
        self.current_time.setFixedWidth(40)
        self.current_time.setAlignment(Qt.AlignCenter)
        self.current_time.setStyleSheet("color: white; font-size: 15px; font-weight: bold; background-color: transparent;")

        self.progress_bar = ClickableSlider(Qt.Horizontal)
        self.progress_bar.setRange(0, self.total_duration)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(350)
        self.progress_bar.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #6A0DAD;
                height: 8px;
                background: #3a3a3a;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #6A0DAD;
                border: 1px solid #4A0D8B;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #8B5FBF;
            }
            QSlider::sub-page:horizontal {
                background: #6A0DAD;
                border-radius: 4px;
            }
        """)

        self.total_time = QLabel("3:45")
        self.total_time.setFixedWidth(40)
        self.total_time.setAlignment(Qt.AlignCenter)
        self.total_time.setStyleSheet("color: white; font-size: 15px; font-weight: bold; background-color: transparent;")

        progress_section.addWidget(self.current_time)
        progress_section.addWidget(self.progress_bar)
        progress_section.addWidget(self.total_time)

        # Control buttons section
        controls_section = QHBoxLayout()
        controls_section.setSpacing(10)
        controls_section.setAlignment(Qt.AlignCenter)

        # Create buttons with text symbols
        self.shuffle = QPushButton("⇄")    # Shuffle symbol
        self.rewind = QPushButton("«")     # Rewind symbol  
        self.skip = QPushButton("»")       # Skip symbol
        self.loop = QPushButton("↻")       # Loop symbol

        # Style the control buttons
        control_buttons_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #8B5FBF;
            }
            QPushButton:pressed {
                color: #4A0D8B;
            }
        """

        # Set button sizes and styles for control buttons
        for button in [self.rewind, self.skip]:
            button.setFixedSize(60, 35)
            button.setStyleSheet(control_buttons_style)

        self.shuffle.setStyleSheet(self.inactive_style)
        self.loop.setStyleSheet(self.inactive_style)

        # Create separate play and pause buttons
        self.play_button = QPushButton("▶")
        self.pause_button = QPushButton("▐▐")

        # Style the play button
        self.play_button.setFixedSize(70, 40)
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 65px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #8B5FBF;
            }
            QPushButton:pressed {
                color: #4A0D8B;
            }
        """)

        # Style the pause button
        self.pause_button.setFixedSize(70, 40)
        self.pause_button.setStyleSheet("""
            QPushButton {
                padding-right: 10px;
                background-color: transparent;
                border: none;
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #8B5FBF;
            }
            QPushButton:pressed {
                color: #4A0D8B;
            }
        """)

        # Initially show play button and hide pause button
        self.pause_button.setVisible(False)

        controls_section.addWidget(self.shuffle)
        controls_section.addWidget(self.rewind)
        controls_section.addWidget(self.play_button)
        controls_section.addWidget(self.pause_button)
        controls_section.addWidget(self.skip)
        controls_section.addWidget(self.loop)

        # Volume section
        volume_section = QHBoxLayout()
        volume_section.setSpacing(15)
        volume_section.setAlignment(Qt.AlignCenter)
        
        # Add left stretch to push content to center
        volume_section.addStretch(1)

        self.volume_icon = QPushButton("♪")  # Volume symbol
        self.volume_icon.setFixedSize(20, 20)
        self.volume_icon.setStyleSheet(control_buttons_style)

        self.volume_bar = ClickableSlider(Qt.Horizontal)
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setValue(100)
        self.volume_bar.setFixedWidth(120)
        self.volume_bar.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #6A0DAD;
                height: 6px;
                background: #3a3a3a;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6A0DAD;
                border: 1px solid #4A0D8B;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #8B5FBF;
            }
            QSlider::sub-page:horizontal {
                background: #6A0DAD;
                border-radius: 3px;
            }
        """)

        volume_section.addWidget(self.volume_icon)
        volume_section.addWidget(self.volume_bar)
        
        # Add right stretch to push content to center
        volume_section.addStretch(1)

        # Add all sections to middle container
        middle_container.addLayout(progress_section)
        middle_container.addLayout(controls_section)
        middle_container.addLayout(volume_section)

        # Add the smaller bordered container to content layout
        content_layout.addWidget(middle_container_widget)
        content_layout.addStretch(1)

        # Create timer for updating progress
        self.timer = QTimer()
        self.timer.setInterval(1000)

    def load_first_song_paused(self):
        # Load the first song in paused state on startup
        playlist = self.music_player.get_playlist()

        if not playlist:
            return

        # Load first song whithout playing it permanently
        success, song_name = self.music_player.play_song(0)

        if success:
            # Immediately pause it
            self.music_player.pause_song()

            self.is_playing = False
            self.was_paused = True
            self.current_position = 0

            # Show play button
            self.pause_button.setVisible(False)
            self.play_button.setVisible(True)

            # Update UI properly
            self.update_song_display()
            self.status.setText("Ready")

            # Ensure timer is stopped
            self.timer.stop()

    def update_playlist_ui(self, playlist, added_files=None):
        # Update the sidebar song list without breaking layout

        layout = self.scroll_layout

        # Remove only the song buttons and keep label and spacer
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)

            # Skip spacer
            if item.spacerItem():
                continue

            widget = item.widget()
            if isinstance(widget, QPushButton):
                widget.deleteLater()

        # Re-add songs BEFORE the spacer
        for i, song in enumerate(playlist):
            song_name = song.replace(".mp3", "")

            song_btn = QPushButton(f"▶ {song_name}")
            song_btn.setMaximumWidth(328)
            song_btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 6px;
                    border: 1px solid #6A0DAD;
                    border-radius: 3px;
                    background-color: transparent;
                    font-size: 11px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: rgba(58, 58, 58, 0.7);
                    border: 1px solid #8B5FBF;
                }
            """)

            song_btn.clicked.connect(
                lambda checked, idx=i: self.play_specific_song(idx)
            )

            # Insert ABOVE spacer
            layout.insertWidget(layout.count() - 1, song_btn)

        self.track_count.setText(f"{len(playlist)} Tracks")

    def play_previous_song(self):
        if self.loop_check:
            self.music_player.loop_song()
        elif self.shuffle_check:  
             self.music_player.shuffle_backward()
        else:
            self.music_player.previous_song()
        self.was_paused = False
        self.start_playback()
    
    active_style = """
        QPushButton {
            background-color: transparent;
            border: none;
            color: #6A0DAD;
            font-size: 24px;
            font-weight: bold;
        }
        QPushButton:hover {
            color: #8B5FBF;
        }
        """
    
    inactive_style = """
        QPushButton {
            background-color: transparent;
            border: none;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
        QPushButton:hover {
            color: #8B5FBF;
        }
        QPushButton:pressed {
            color: #4A0D8B;
        }
        """

    def loop_value_changer(self):
        self.loop_check = not self.loop_check

        if self.loop_check:
            self.loop.setStyleSheet(self.active_style)
            self.status.setText("Loop: ON")
        else:
            self.loop.setStyleSheet(self.inactive_style)
            self.status.setText("Loop: OFF")

    def shuffle_value_changer(self):
        self.shuffle_check = not self.shuffle_check
        self.music_player.toggle_shuffle()

        if self.shuffle_check:
            self.shuffle.setStyleSheet(self.active_style)
            self.status.setText("shuffle: ON")
        else:
            self.shuffle.setStyleSheet(self.inactive_style)
            self.status.setText("shuffle: OFF")

    def toggle_webcam_page(self):
        # If webcam window already open then close it
        if self.webcamWindow is not None and self.webcamWindow.isVisible():
            self.webcamWindow.close()
            self.webcamWindow = None
            print("Webcam page closed")
            return

        # Otherwise open webcam window
        from webCam import WebcamWindow
        self.webcamWindow = WebcamWindow(self)
        self.webcamWindow.resize(800, 600)
        self.webcamWindow.show()
        print("Webcam page opened")

    def setup_connections(self):
        # Connect signals
        self.back.clicked.connect(self.open_front_page)
        self.folder.clicked.connect(self.toggle_drag_drop_window)
        self.settings.clicked.connect(self.toggle_settings_page)
        self.hand.clicked.connect(self.toggle_webcam_page)
        self.rewind.clicked.connect(self.rewind_func)
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.pause_button.clicked.connect(self.toggle_play_pause)
        self.skip.clicked.connect(self.play_next_song)
        self.loop.clicked.connect(self.loop_value_changer)
        self.shuffle.clicked.connect(self.shuffle_value_changer)
        self.timer.timeout.connect(self.update_playback)
        self.volume_icon.clicked.connect(self.mute)
        self.progress_bar.sliderMoved.connect(self.on_slider_moved)
        self.progress_bar.sliderReleased.connect(self.on_slider_released)
        self.volume_bar.clicked.connect(self.on_volume_bar_clicked)
        self.volume_bar.valueChanged.connect(self.on_volume_changed)
        self.volume_bar.valueChanged.connect(self.update_volume_display)

    def update_album_art(self):
        # Update the album art display with the current song's artwork
        album_art_path = self.music_player.current_album_art
        
        try:
            if album_art_path and os.path.exists(album_art_path):
                # Load and scale the album art
                self.mediaImage.setIcon(QIcon(album_art_path))
                
                # Adjust icon size to fit the container
                with Image.open(album_art_path) as img:
                    width, height = img.size
                    # Calculate size to maintain aspect ratio and fit in 412x412
                    if width > height:
                        new_width = 412
                        new_height = int((412 / width) * height)
                    else:
                        new_height = 412
                        new_width = int((412 / height) * width)
                    
                    self.mediaImage.setIconSize(QSize(new_width, new_height))
            else:
                # Use default image
                self.mediaImage.setIcon(QIcon("images/glasses.jpg"))
                self.mediaImage.setIconSize(QSize(300, 300))
                
        except Exception as e:
            print(f"Error loading album art: {e}")
            # Fallback to default image
            self.mediaImage.setIcon(QIcon("images/glasses.jpg"))
            self.mediaImage.setIconSize(QSize(300, 300))

    def play_specific_song(self, song_index):
        # Play a specific song from the playlist
        success, song_name = self.music_player.play_song(song_index)
        if success:
            self.is_playing = True
            self.play_button.setVisible(False)
            self.pause_button.setVisible(True)
            self.timer.start()
            
            # Update song info and album art
            self.update_song_display()
            self.status.setText(f"Playing: {song_name}")
        else:
            self.status.setText("Error playing song")

    def update_song_display(self):
        # Update all song-related displays

        # If no song has been played yet, show prompt
        if not self.music_player.is_playing and not self.music_player.was_paused:
            self.mediaTitle.setText("Press Play to Start")
            self.mediaArtist.setText("")
            self.mediaImage.setIcon(QIcon("images/glasses.jpg"))
            self.mediaImage.setIconSize(QSize(300, 300))
            self.progress_bar.setValue(0)
            self.current_time.setText("0:00")
            self.total_time.setText("0:00")
            return

        song_name, artist = self.music_player.get_current_song_info()
        self.mediaTitle.setText(song_name)
        self.mediaArtist.setText(artist)
        
        # Update album art
        self.update_album_art()
        
        # Update progress bar and time
        self.total_duration = self.music_player.current_song_length
        self.progress_bar.setRange(0, self.total_duration)
        self.current_position = 0
        self.progress_bar.setValue(0)
        
        minutes = self.total_duration // 60
        seconds = self.total_duration % 60
        self.total_time.setText(f"{minutes}:{seconds:02d}")
        self.update_time_display()
    
    def refresh_playlist(self, added_files=None):
        # Refresh playlist after adding new songs
        self.music_player.load_playlist()
        playlist = self.music_player.get_playlist()
        self.update_playlist_ui(playlist, added_files)

    def on_volume_bar_clicked(self, value):
        # Handle when volume bar is clicked directly
        if self.muted == 1:
            self.unmute_with_volume(value)

    def on_volume_changed(self, value):
        # Handle when volume is changed via dragging or other methods
        if self.muted == 1 and value > 0:
            self.unmute_with_volume(value)

    def unmute_with_volume(self, volume):
        # Unmute and set to specified volume
        self.muted = 0
        self.volume_icon.setText("♪") 
        self.saved_volume = volume

    def close_settings_page(self):
        if self.settings_page:
            self.settings_page.close()
            self.settings_page = None
            print("Settings page closed")
    
    def close_webcam_page(self):
        if self.webcamWindow is not None:
            self.webcamWindow.close()
            self.webcamWindow = None
            print("Webcam page closed")

    def open_front_page(self):
        self.close_settings_page()
        self.close_webcam_page()
        self.stop_playback()
        self.controller.setCurrentIndex(0)
    
    def toggle_drag_drop_window(self):
        if self.drag_drop_window is not None and self.drag_drop_window.isVisible():
            self.drag_drop_window.close()
            self.drag_drop_window = None
            print("Drag-and-drop window closed")
            return

        try:
            self.drag_drop_window = DragDropWindow(
                self.songs_folder,
                on_files_added=self.refresh_playlist
            )
            self.drag_drop_window.show()
            print("Drag-and-drop window opened")
        except Exception as e:
            print(f"Error opening drag-and-drop window: {e}")

    def toggle_settings_page(self):

        # Close if already open
        if self.settings_page and self.settings_page.isVisible():
            self.close_settings_page()
            return

        self.open_settings_page()

    def open_settings_page(self):
        if self.settings_page is None:
            self.settings_page = SettingsPage(None)
            self.settings_page.setWindowFlag(Qt.Window, True)

        self.settings_page.show()
        self.settings_page.raise_()
        self.settings_page.activateWindow()

    def rewind_func(self):
        now = time.monotonic()

        # If less than 5 seconds into song then always go to previous
        if self.current_position < 5:
            self.last_rewind_click = 0
            
            # Go to previous track
            self.play_previous_song()
            
            # Sync UI just like play_next_song()
            self.current_position = 0
            self.progress_bar.setValue(0)
            self.update_song_display()
            
            return

        # Double click, previous song
        if now - self.last_rewind_click <= self.REWIND_DOUBLE_CLICK_THRESHOLD:
            self.last_rewind_click = 0
            
            self.play_previous_song()
            
            # Sync UI
            self.current_position = 0
            self.progress_bar.setValue(0)
            self.update_song_display()
            
            return

        # Otherwise, single click (restart current song)
        self.last_rewind_click = now

        if self.current_position > 0:
            self.current_position = 0
            self.music_player.seek(0)
            self.progress_bar.setValue(0)
            self.update_time_display()

    def mute(self):
        if self.muted == 0:
            self.saved_volume = self.volume_bar.value()
            self.volume_bar.setValue(0)
            self.muted = 1
            self.volume_icon.setText("⊘")
        else:
            self.volume_bar.setValue(self.saved_volume)
            self.muted = 0
            self.volume_icon.setText("♪")

    def update_time_display(self):
        minutes = self.current_position // 60
        seconds = self.current_position % 60
        self.current_time.setText(f"{minutes}:{seconds:02d}")

    def update_progress(self):
        self.progress_bar.setValue(self.current_position)

    def update_playback(self):
        if not self.is_playing:
            return

        # DO NOT change time if user is dragging
        if self.progress_bar.isSliderDown():
            return

        if self.current_position < self.total_duration:
            self.current_position += 1
            self.progress_bar.blockSignals(True)
            self.progress_bar.setValue(self.current_position)
            self.progress_bar.blockSignals(False)
            self.update_time_display()
        else:
            self.play_next_song()

    def toggle_play_pause(self):
        if not self.is_playing:
            self.start_playback()
        else:
            self.pause_playback()

    def start_playback(self):
        # Start or resume music
        # incase the fist gesture is already detected
        if self.is_playing:
            return

        # Resume from pause
        if self.was_paused:
            self.music_player.unpause_song()
            self.was_paused = False
            self.is_playing = True

            self.play_button.setVisible(False)
            self.pause_button.setVisible(True)
            self.timer.start()
            self.status.setText("Playing")
            return

        # Otherwise start from beginning
        success, song_name = self.music_player.play_song()
        if success:
            self.is_playing = True
            self.play_button.setVisible(False)
            self.pause_button.setVisible(True)
            self.timer.start()

            self.update_song_display()
            self.status.setText(f"Playing: {song_name}")
        else:
            self.status.setText("Error playing music")

    def pause_playback(self):
        # Pause the music
        self.music_player.pause_song()
        self.was_paused = True
        self.pause_position = self.current_position

        self.is_playing = False
        self.pause_button.setVisible(False)
        self.play_button.setVisible(True)
        self.timer.stop()
        self.status.setText("Paused")

    def stop_playback(self):
        # Stop the music
        self.music_player.stop_song()
        self.is_playing = False
        # Show play button, hide pause button
        self.pause_button.setVisible(False)
        self.play_button.setVisible(True)
        self.timer.stop()
        self.current_position = 0
        self.progress_bar.setValue(0)
        self.update_time_display()
        self.was_paused = False
        self.pause_position = 0
        self.status.setText("Stopped")

    def play_next_song(self):
        # Play the next song in playlist
        self.was_paused = False
        if self.loop_check:
            success, song_name = self.music_player.loop_song()
        elif self.shuffle_check:
            success, song_name = self.music_player.shuffle_forward()
        else:
            success, song_name = self.music_player.next_song()
        if success:
            self.current_position = 0
            self.progress_bar.setValue(0)
            
            # Update song info and album art
            self.update_song_display()
            self.status.setText(f"Playing: {song_name}")
        else:
            self.stop_playback()

    def on_slider_moved(self, position):
        self.current_position = position
        self.update_time_display()

    def on_slider_released(self):
        self.was_paused = False
        if not self.is_playing:
            return

        self.current_position = self.progress_bar.value()

        self.music_player.seek(self.current_position)

        # Reset timer state so it doesn't jump back
        self.timer.stop()
        self.timer.start()

        self.update_time_display()

    def update_volume_display(self):
        # Update volume based on slider
        volume = self.volume_bar.value()

        if volume == 0:
            self.volume_icon.setText("⊘")
        else:
            self.volume_icon.setText("♪")

        self.music_player.set_volume(volume)
    
    def closeEvent(self, event):
        self.close_settings_page()
        self.close_webcam_page()
        self.stop_playback()
        event.accept()

