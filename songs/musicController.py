import os
import pygame
import threading
import random
from PIL import Image
import io
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()

        self.current_song_index = 0
        self.playlist = []
        self.is_playing = False
        self.current_song_length = 0
        self.current_album_art = None
        self.load_playlist()
        self.paused_at = 0
        self.was_paused = False

        # --- Shuffle additions ---
        self.shuffle_enabled = False
        self.shuffle_history = []  # stores played song indices in order
        # -------------------------

    def load_playlist(self):
        """Load all MP3 files from the music directory (relative to this file)"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.playlist = [
            file for file in os.listdir(self.base_dir)
            if file.endswith('.mp3') and os.path.isfile(os.path.join(self.base_dir, file))
        ]

        self.playlist.sort()
        return self.playlist

    def get_playlist(self):
        return self.playlist

    def get_pause_position_seconds(self):
        if self.was_paused and self.paused_at:
            return int(self.paused_at / 1000)
        return 0

    # ---------------- SHUFFLE CONTROL ----------------

    def toggle_shuffle(self):
        """Enable / Disable shuffle"""
        self.shuffle_enabled = not self.shuffle_enabled

        # When turning shuffle on, start history with current song
        if self.shuffle_enabled:
            self.shuffle_history = [self.current_song_index]

        return self.shuffle_enabled

    def shuffle_forward(self):
        """Get next shuffled song (new random, history-aware)"""
        if not self.playlist:
            return False, "No songs"

        # If only one song, just replay
        if len(self.playlist) == 1:
            return self.play_song(0)

        new_index = self.current_song_index
        while new_index == self.current_song_index:
            new_index = random.randint(0, len(self.playlist) - 1)

        self.current_song_index = new_index
        self.shuffle_history.append(new_index)

        return self.play_song()

    def shuffle_backward(self):
        """Go back to previously shuffled song"""
        if not self.shuffle_history:
            return self.play_song()

        if len(self.shuffle_history) > 1:
            # Remove current
            self.shuffle_history.pop()
            # Previous becomes current
            self.current_song_index = self.shuffle_history[-1]
        else:
            # Only one in history → restart current
            self.current_song_index = self.shuffle_history[0]

        return self.play_song()

    # ------------------------------------------------

    def extract_album_art(self, file_path):
        try:
            audio = MP3(file_path, ID3=ID3)
            if audio.tags is None:
                return None

            for tag in ['APIC:', 'covr', 'APIC']:
                if tag in audio.tags:
                    album_art = audio.tags[tag]
                    if hasattr(album_art, 'data'):
                        image_data = album_art.data
                        image = Image.open(io.BytesIO(image_data))
                        return image

            try:
                tags = ID3(file_path)
                for tag in tags.values():
                    if isinstance(tag, APIC):
                        image_data = tag.data
                        image = Image.open(io.BytesIO(image_data))
                        return image
            except:
                pass

        except Exception as e:
            print(f"Error extracting album art from {file_path}: {e}")

        return None

    def get_album_art_path(self, file_path):
        image = self.extract_album_art(file_path)
        if image:
            try:
                temp_path = "temp_album_art.jpg"
                image.save(temp_path, "JPEG")
                self.current_album_art = temp_path
                return temp_path
            except Exception as e:
                print(f"Error saving album art: {e}")

        self.current_album_art = "images/glasses.jpg"
        return "images/glasses.jpg"

    def play_song(self, song_index=None):
        if not self.playlist:
            return False, "No songs in playlist"

        # If UI manually selected a song → reset shuffle history
        if song_index is not None:
            self.current_song_index = song_index
            if self.shuffle_enabled:
                self.shuffle_history = [song_index]

        if self.current_song_index >= len(self.playlist):
            self.current_song_index = 0

        try:
            current_song = self.playlist[self.current_song_index]
            song_path = os.path.join(self.base_dir, current_song)

            pygame.mixer.music.load(song_path)

            if self.was_paused and self.paused_at > 0:
                pygame.mixer.music.play(start=self.paused_at / 1000.0)
            else:
                pygame.mixer.music.play()

            self.is_playing = True
            self.was_paused = False

            sound = pygame.mixer.Sound(song_path)
            self.current_song_length = int(sound.get_length())

            self.get_album_art_path(song_path)

            return True, current_song

        except Exception as e:
            print(f"Error playing song: {e}")
            return False, str(e)

    def pause_song(self):
        if self.is_playing:
            self.paused_at = pygame.mixer.music.get_pos()
            pygame.mixer.music.pause()
            self.is_playing = False
            self.was_paused = True

    def unpause_song(self):
        pygame.mixer.music.unpause()
        self.is_playing = True

    def stop_song(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.paused_at = 0
        self.was_paused = False

    # --- Normal non-shuffle next/previous ---

    def next_song(self):
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
        return self.play_song()

    def previous_song(self):
        self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
        return self.play_song()

    # ----------------------------------------

    def loop_song(self):
        return self.play_song()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume / 100.0)

    def seek(self, position_seconds):
        if not self.playlist:
            return

        current_song = self.playlist[self.current_song_index]
        song_path = os.path.join(self.base_dir, current_song)

        pygame.mixer.music.stop()
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(start=float(position_seconds))

        self.is_playing = True
        self.paused_at = None

    def get_current_song_info(self):
        if not self.playlist or self.current_song_index >= len(self.playlist):
            return "No Song", "Unknown Artist"

        song_name = self.playlist[self.current_song_index]

        try:
            audio = MP3(song_name, ID3=ID3)
            title = ""
            artist = ""
            
            base_name = song_name.replace('.mp3', '')
            if ' - ' in base_name:
                title, artist = base_name.split(' - ', 1)
            else:
                title = base_name
                artist = "Unknown Artist"

            return title, artist

        except Exception as e:
            print(f"Error reading metadata: {e}")
            base_name = song_name.replace('.mp3', '')
            if ' - ' in base_name:
                artist, title = base_name.split(' - ', 1)
                return title, artist
            else:
                return base_name, "Unknown Artist"


# Global instance
music_player = MusicPlayer()
