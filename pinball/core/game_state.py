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

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
    # from core.modbus_api import ModbusAPI
    # from core.sound_api import SoundAPI
    # from core.screen_api import ScreenAPI
    # from core.event_api import EventAPI

class GameStateController:
    """
    Manages the overall state of the game and transitions based on events
    registered with the GameEventSystem to respond to game input events.
    """
    def __init__(self,
                 screen_api,
                 event_api,
                 modbus_api,
                 sound_api):
        """
        Initializes the GameStateController with the necessary APIs.
        :param screen_api: Instance of PinballScreenAPI for screen updates.
        :param event_system: Instance of GameEventSystem for event handling.
        :param modbus_api: Instance of ModbusClientAPI for Modbus communication.
        :param sound_api: Instance of SoundAPI for sound playback.
        """
        self.screen_api = screen_api
        self.event_api = event_api
        self.modbus_api = modbus_api
        self.sound_api = sound_api
        
        self.state = "attract"
        self.previous_state = 'attract'
        self.score = 0
        self.num_balls = 3
        self.current_ball = 1
        self.game_over_elapsed_time = 0

        self.last_sling_time = 0
        print(f"[GameStateController] Initialized with state: {self.state}")

    def handle_event(self, event_name: str):
        print(f"[GameStateController] Handling event: {event_name}")

        # attract state
        if self.state == "attract":
            
            # get music playing if not already
            if pygame.mixer.music.get_busy() is False:
                self.sound_api.set_background_music("fight_song.wav", volume=1.0)

            # check if event is start_button_pressed
            if event_name == "start_button_pressed":
                print("Transitioning to play mode")
                self.state = "play"
                self.sound_api.set_background_music("pinball_wizard.wav", volume=1.0)

                self.score = 0
                self.modbus_api.write_value("drop_target_reset", True)
                self.modbus_api.write_value("load_ball", True)
            # reset previous state
            if self.previous_state != 'attract':
                self.previous_state = 'attract'

        # play state
        elif self.state == "play":

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
                    
            if self.previous_state == 'attract':
                self.previous_state = 'play'

        # game over state
        elif self.state == "game_over":
            if event_name == "start_button_pressed":
                print("Restarting game")
                self.state = "play"
                self.previous_state = 'game_over'

            elif event_name == "game_over_timeout":
                print("Transitioning to attract state")
                self.state = "attract"
                self.previous_state = 'game_over'

            if self.state == "attract" or self.state == "play":
                self.score = 0
                self.game_over_elapsed_time = 0

    def update(self, delta_time: int):
        print("[GameStateController] reading all values")
        all_values = self.modbus_api.read_all()

        # Check for low start_button coil
        print("[GameStateController] Checking start button")
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
                    self.sound_api.play("chaching")
                    print(f"[DEBUG] Scored {delta} hits from {name} x {device.score}")
                total += count * device.score
                device.starting_count = count  # Update stored count

        # print(f"[GameStateController] Updated score: {total}")
        self.score = total

    # def maybe_play_sling(self):
    #     now = time.time()
    #     if now - self.last_sling_time > self.sling_cooldown:
    #         self.sound_api.play("sling")
    #         self.last_sling_time = now

    def get_state(self):
        return self.state

    def get_ball(self):
        return self.current_ball

    def get_score(self):
        return self.score
