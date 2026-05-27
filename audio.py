"""
Audio-Modul für Pygame.
Spielt MP3-Dateien aus dem artwork/-Ordner ab, falls vorhanden.
"""

import pygame
import os
from pathlib import Path

class AudioManager:
    """
    Verwaltet die Audio-Wiedergabe für das Spiel.
    Lädt automatisch MP3-Dateien aus dem artwork/-Ordner.
    """

    def __init__(self, artwork_dir: str = "interfaces/renderer/pygame/artwork"):
        """
        Initialisiert den Audio-Manager.
        Sucht nach MP3-Dateien im artwork/-Ordner und lädt sie.

        Args:
            artwork_dir: Pfad zum Ordner mit Audio-Dateien.
        """
        self.artwork_dir = Path(artwork_dir)
        self.sounds = {}
        self.music = None
        self.music_volume = 0.5  # Standard-Lautstärke (0.0-1.0)
        self.sfx_volume = 0.7

        pygame.mixer.init()
        self._load_audio_files()

    def _load_audio_files(self) -> None:
        """Lädt alle MP3-Dateien aus dem artwork/-Ordner."""
        if not self.artwork_dir.exists():
            return

        for mp3_file in self.artwork_dir.glob("*.mp3"):
            try:
                # Dateiname ohne Endung als Key
                sound_name = mp3_file.stem
                self.sounds[sound_name] = pygame.mixer.Sound(str(mp3_file))
                print(f"Geladene Audio-Datei: {sound_name}")
            except Exception as e:
                print(f"Fehler beim Laden von {mp3_file}: {e}")

        # Hintergrundmusik (falls eine Datei mit "music" im Namen existiert)
        music_files = list(self.artwork_dir.glob("*music*.mp3"))
        if music_files:
            self.music = pygame.mixer.music.load(str(music_files[0]))
            pygame.mixer.music.set_volume(self.music_volume)

    def play_music(self, loop: bool = True) -> None:
        """Spielt die Hintergrundmusik ab (falls vorhanden)."""
        if self.music:
            pygame.mixer.music.play(loops=-1 if loop else 0)

    def stop_music(self) -> None:
        """Stoppt die Hintergrundmusik."""
        pygame.mixer.music.stop()

    def play_sound(self, sound_name: str) -> None:
        """
        Spielt einen Soundeffekt ab.

        Args:
            sound_name: Name des Sounds (ohne .mp3-Endung).
        """
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(self.sfx_volume)
            self.sounds[sound_name].play()

    def set_music_volume(self, volume: float) -> None:
        """Setzt die Lautstärke der Musik (0.0-1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume: float) -> None:
        """Setzt die Lautstärke der Soundeffekte (0.0-1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))