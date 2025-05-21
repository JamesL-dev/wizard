import pygame
import os

from typing import Dict

class SoundAPI:
    def __init__(self, sound_dir="assets/sounds"):
        pygame.mixer.init()
        pygame.mixer.init()
        print(f"[DEBUG] Mixer initialized: {pygame.mixer.get_init()}")

        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_dir: str = sound_dir
        # self.sound_dir: str = os.abspath(os.join(os.path.dirname(__file__), "..", sound_dir))

    def load_sound(self, name, filename):
        path = os.path.join(self.sound_dir, filename)
        if os.path.exists(path):
            self.sounds[name] = pygame.mixer.Sound(path)
            print(f"[DEBUG] Sound loaded: {name} from {path}")
        else:
            raise FileNotFoundError(f"Sound file not found: {path}")

    def play(self, name):
        if name in self.sounds:
            print(f"[DEBUG] Playing sound: {name}")
            self.sounds[name].play()
        else:
            print(f"[SoundManager] No sound loaded with name '{name}'.")

    def stop(self, name):
        if name in self.sounds:
            print(f"[DEBUG] Stopping sound: {name}")
            self.sounds[name].stop()
            
    def set_volume(self, name, volume):
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
        else:
            print(f"[SoundManager] No sound loaded with name '{name}'.")
    
    def set_background_music(self, filename: str, volume: float = 1.0):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        print(f"[DEBUG] Setting background music: {filename} with volume {volume}")
        path = os.path.join(self.sound_dir, filename)
        if not os.path.exists(path):
            print(f"[ERROR] Background music file not found: {path}")
            return
        try:
            pygame.mixer.music.load(path)
            print(f"[DEBUG] Background music loaded: {filename} from {path}")
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            print(f"[DEBUG] Game music playback started.")
        except Exception as e:
            print(f"[ERROR] Failed to play background music: {e}")


    def stop_background_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        print(f"[DEBUG] Game music playback stopped.")