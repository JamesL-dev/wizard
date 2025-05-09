"""
Game State Controller
=====================

This module defines the Game State Controller class.
This module is the primary game class that will handle
changing the game state based on certain events and
triggering other modules to update to new values.
This also will trigger state change in the PLC directly.

Author: Kevin Wing
Project: University of Idaho PLC Pinball
Last Updated: 4/17/2025
"""

import time
import pygame
import os
import time
# previous_state = 'attract'

class GameStateController:
    """
    Manages the overall state of the game and transitions based on events.
    Registered with the GameEventSystem to respond to game input events.
    Also manages scoring logic while in 'play' mode.
    """
    def __init__(self, screen_api, event_system, modbus_api, sound_manager):
        import os  # ensure os is available for file checks

        self.state = "attract"
        self.previous_state = 'attract'
        self.score = 0
        self.screen_api = screen_api
        self.event_system = event_system
        self.modbus_api = modbus_api
        self.sound_manager = sound_manager
        self.num_balls = 3
        self.current_ball = 1
        self.game_over_elapsed_time = 0

        self.last_sling_time = 0

        # Start attract mode music at init
        # full_path = os.path.abspath("assets/sounds/fight_song.mp3")
        base_dir = os.path.dirname(__file__)
        full_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "sounds", "fight_song.wav"))

        print(f"[DEBUG] Trying to load attract music: {full_path}")
        print(f"[DEBUG] File exists: {os.path.exists(full_path)}")
        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1)
            print("[DEBUG] Attract music playback started at init.")
        except Exception as e:
            print("[ERROR] Failed to play attract music at init:", e)
        self.sling_cooldown = 0.5  # seconds

    def handle_event(self, event_name: str):
        print(f"[GameStateController] Handling event: {event_name}")

        # attract state
        if self.state == "attract":
            if pygame.mixer.music.get_busy() is False:
                full_path = os.path.abspath("assets/sounds/fight_song.wav")
                print(f"[DEBUG] Trying to load: {full_path}")
                print(f"[DEBUG] File exists: {os.path.exists(full_path)}")
                try:
                    pygame.mixer.music.load(full_path)
                    pygame.mixer.music.play(-1)
                    print("[DEBUG] Music playback started in attract mode.")
                except Exception as e:
                    print("[ERROR] Failed to play music in attract mode:", e)

            if event_name == "start_button_pressed":
                print("Transitioning to play mode")
                self.state = "play"
                pygame.mixer.music.stop()
                try:
                    base_dir = os.path.dirname(__file__)
                    game_song_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "sounds", "pinball_wizard.wav"))
                    pygame.mixer.music.load(game_song_path)
                    pygame.mixer.music.set_volume(1.0)
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print("[ERROR] Could not load gameplay theme:", e)

                self.score = 0
                self.modbus_api.write_value("drop_target_reset", True)
                self.modbus_api.write_value("load_ball", True)
                # load ball
                # self.modbus_api.client.write_single_coil(1, True)
                # self.modbus_api.client.write_single_coil(4, True)
                # self.sound_manager.play("start")
                pass  # already started in __init__, no need to restart

        # play state
        elif self.state == "play":
            if self.previous_state == 'attract':
                # self.modbus_api.client.write_single_coil(1, True)
                # self.modbus_api.client.write_single_coil(2, True)
                # self.modbus_api.write_value("drop_target_reset", True)
                # self.modbus_api.write_value("load_ball", True)
                self.previous_state = 'play'

            # update score based on registers
            # self.update_score()
            # # play effect sound with throttle
            # if event_name == "sling_left_pressed":
            #     self.maybe_play_sling()

            # check if event is ball_drain and lose condition
            if event_name == "ball_drain_pressed":
                print("Ball drained")
                current_ball = self.modbus_api.read_value('ball_drain')
                if current_ball < self.num_balls:
                    # self.current_ball += 1
                    print(f"Ball {self.current_ball}")
                    self.modbus_api.write_value("load_ball", True)
                else:
                    print("Game Over")
                    self.state = "game_over"
                    self.previous_state = 'play'
                    self.game_over_elapsed_time = 0
                    self.modbus_api.write_value("game_over_bit", True)
                    time.sleep(10)
                    
                    # self.sound_manager.play("game_over")
                    # pygame.mixer.music.stop()

        # game over state
        elif self.state == "game_over":
            if event_name == "start_button_pressed":
                print("Restarting game")
                self.state = "play"
                self.previous_state = 'game_over'
                # self.sound_manager.play("fight_song")
                # if pygame.mixer.music.get_busy():
                #     pygame.mixer.music.stop()
                # pygame.mixer.music.load("assets/sounds/fight_song.mp3")
                # pygame.mixer.music.play(-1)
            elif event_name == "game_over_timeout":
                print("Transitioning to attract state")
                self.state = "attract"
                self.previous_state = 'game_over'

            if self.state == "attract" or self.state == "play":
                self.score = 0
                self.game_over_elapsed_time = 0

    def update(self, delta_time: int):
        all_values = self.modbus_api.read_all()

        # Check for low start_button coil
        start_button_val = all_values.get("start_button", 1)  # assume 1 if missing
        if self.state == "play" and start_button_val == 0:
            print("[GameStateController] Start button released — returning to attract mode")
            self.state = "attract"
            self.previous_state = "play"
            self.score = 0
            self.current_ball = 1
            self.game_over_elapsed_time = 0
            return  # skip further updates this tick

        if self.state == "play":
            self.update_score()

    def update_score(self):
        total = 0
        all_values = self.modbus_api.read_all()
        for name, device in self.modbus_api.devices.items():
            if device.direction == "input" and device.reg_type in ("input_register", "holding_register"):
                count = all_values.get(name, 0)
                delta = count - device.starting_count
                if delta > 0:
                    self.sound_manager.play("chaching")
                    print(f"[DEBUG] Scored {delta} hits from {name} x {device.score}")
                total += count * device.score
                device.starting_count = count  # Update stored count

        # print(f"[GameStateController] Updated score: {total}")
        self.score = total

    def maybe_play_sling(self):
        now = time.time()
        if now - self.last_sling_time > self.sling_cooldown:
            self.sound_manager.play("sling")
            self.last_sling_time = now

    def get_state(self):
        return self.state

    def get_ball(self):
        return self.current_ball

    def get_score(self):
        return self.score
