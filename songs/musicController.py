import os
import pygame
import random
import time
from PIL import Image
import io
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


class MusicPlayer:
    def __init__(self):
        self.init_mixer_safe()

        self.current_song_index = 0
        self.playlist = []
        self.is_playing = False
        self.current_song_length = 0
        self.current_album_art = None

        # Track paused positions per song
        self.paused_positions = {}

        self.was_paused = False
        self.shuffle_enabled = False
        self.shuffle_history = []

        self.load_playlist()

    # mixer initializer
    def init_mixer_safe(self):
        try:
            pygame.mixer.init()
        except Exception:
            print("Audio init failed, retrying...")
            time.sleep(1)
            try:
                pygame.mixer.init()
            except Exception as e:
                print("Mixer failed completely:", e)

    # Playlist
    def load_playlist(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.playlist = [
            f for f in os.listdir(self.base_dir)
            if f.endswith(".mp3") and os.path.isfile(os.path.join(self.base_dir, f))
        ]
        self.playlist.sort()
        return self.playlist

    def get_playlist(self):
        return self.playlist

    # Shuffle
    def toggle_shuffle(self):
        self.shuffle_enabled = not self.shuffle_enabled
        if self.shuffle_enabled:
            self.shuffle_history = [self.current_song_index]
        return self.shuffle_enabled

    # Load + Seek songs
    def _load_and_seek(self, index=None, position=None, play=False):
        if not self.playlist:
            return False, "No songs"

        # Song switching
        if index is not None:
            if index != self.current_song_index:
                # Reset paused position for the new song
                self.current_song_index = index
                self.paused_positions[self.current_song_index] = 0.0
            else:
                self.current_song_index = index

            if self.shuffle_enabled:
                self.shuffle_history = [self.current_song_index]

        # Ensure position is correct
        if position is None:
            position = self.paused_positions.get(self.current_song_index, 0.0)

        song = self.playlist[self.current_song_index]
        path = os.path.join(self.base_dir, song)

        try:
            current_vol = pygame.mixer.music.get_volume()

            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)

            if play:
                pygame.mixer.music.play(start=float(position))
                self.is_playing = True
                self.was_paused = False
            else:
                pygame.mixer.music.set_volume(0)
                pygame.mixer.music.play(start=float(position))
                pygame.mixer.music.pause()
                pygame.mixer.music.set_volume(current_vol)

                self.was_paused = True
                self.is_playing = False

            # Store current paused position
            self.paused_positions[self.current_song_index] = float(position)

            # length of song
            sound = pygame.mixer.Sound(path)
            self.current_song_length = int(sound.get_length())

            self.get_album_art_path(path)

            return True, song

        except Exception as e:
            return False, str(e)

    # Controls
    def play_song(self, song_index=None):
        return self._load_and_seek(index=song_index, play=True)

    def pause_song(self):
        if self.is_playing:
            self.paused_positions[self.current_song_index] = pygame.mixer.music.get_pos() / 1000.0
            pygame.mixer.music.pause()
            self.is_playing = False
            self.was_paused = True

    def unpause_song(self):
        pygame.mixer.music.unpause()
        self.is_playing = True

    def stop_song(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.was_paused = False
        self.paused_positions[self.current_song_index] = 0.0

    # Navigation
    def next_song(self, is_playing):
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
        return self._load_and_seek(position=0.0, play=is_playing)

    def previous_song(self, is_playing):
        self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
        return self._load_and_seek(position=0.0, play=is_playing)

    def loop_song(self, is_playing):
        return self._load_and_seek(position=0.0, play=is_playing)

    # Shuffle navigation
    def shuffle_forward(self, is_playing):
        if len(self.playlist) <= 1:
            return self._load_and_seek(position=0.0, play=is_playing)

        new_index = self.current_song_index
        while new_index == self.current_song_index:
            new_index = random.randint(0, len(self.playlist) - 1)

        self.current_song_index = new_index
        self.shuffle_history.append(new_index)

        return self._load_and_seek(position=0.0, play=is_playing)

    def shuffle_backward(self, is_playing):
        if len(self.shuffle_history) > 1:
            self.shuffle_history.pop()
            self.current_song_index = self.shuffle_history[-1]

        return self._load_and_seek(position=0.0, play=is_playing)

    # Seek
    def seek(self, position_seconds, is_playing):
        return self._load_and_seek(position=position_seconds, play=is_playing)

    # Volume
    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume / 100.0)

    # Album Art
    def extract_album_art(self, file_path):
        try:
            audio = MP3(file_path, ID3=ID3)
            if audio.tags:
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        return Image.open(io.BytesIO(tag.data))
        except:
            pass
        return None

    def get_album_art_path(self, file_path):
        image = self.extract_album_art(file_path)
        if image:
            temp_path = "temp_album_art.jpg"
            image.save(temp_path, "JPEG")
            self.current_album_art = temp_path
            return temp_path

        self.current_album_art = "images/error.png"
        return "images/error.png"

    # Song Info
    def get_current_song_info(self):
        if not self.playlist:
            return "No Song", "Unknown Artist"

        song = self.playlist[self.current_song_index]
        name = song.replace(".mp3", "")

        if " - " in name:
            title, artist = name.split(" - ", 1)
        else:
            title = name
            artist = "Unknown Artist"

        return title, artist


# global instance
music_player = MusicPlayer()