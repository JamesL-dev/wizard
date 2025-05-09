import pygame
import os

class SoundManager:
    def __init__(self, sound_dir="wizard_pinball/assets/sounds"):
        pygame.mixer.init()
        pygame.mixer.init()
        print(f"[DEBUG] Mixer initialized: {pygame.mixer.get_init()}")

        self.sounds = {}
        self.sound_dir = sound_dir

    def load_sound(self, name, filename):
        path = os.path.join(self.sound_dir, filename)
        if os.path.exists(path):
            self.sounds[name] = pygame.mixer.Sound(path)
        else:
            raise FileNotFoundError(f"Sound file not found: {path}")

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"[SoundManager] No sound loaded with name '{name}'.")

    def stop(self, name):
        if name in self.sounds:
            self.sounds[name].stop()
