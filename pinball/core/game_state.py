"""
G#ame State Controller
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

from core.high_scores import HighScoreManager


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
        self.last_score = 0
        self.num_balls = 3
        self.current_ball = 0
        self.game_over_elapsed_time = 0
        
        self.active_balls = 0
        self.high_scores = HighScoreManager(filepath=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "scores", "high_scores.json")))
        self.awaiting_high_score = False
        print(f"[GameStateController] High scores loaded: {self.high_scores.get_scores()}")

        self.sound_api.set_background_music("fight_song.wav", volume=0.5)
        # self.last_sling_time = 0
        print(f"[GameStateController] Initialized with state: {self.state}")

    def handle_event(self, event_name: str):
        print(f"[GameStateController] Current state: {self.state}")
        print(f"[GameStateController] Handling event: {event_name}")
        

        # attract state
        if self.state == "attract":
            # if pygame.mixer.music.get_busy() is False:
            #     self.sound_api.set_background_music("fight_song.wav", volume=0.5)
            if self.previous_state == 'game_over' or self.previous_state == 'play':
                self.previous_state = 'attract'
            # get music playing if not already
            # if pygame.mixer.music.get_busy() is False:
            #     self.sound_api.set_background_music("fight_song.wav", volume=1.0)

            # check if event is start_button_pressed
            if event_name == "start_button_pressed":
                print("Transitioning to play mode")
                self.state = "play"
                self.previous_state = 'attract'
                # self.sound_api.set_background_music("pinball_wizard.wav", volume=0.5)

                self.score = 0
                self.modbus_api.write_value("drop_target_reset", True)
                self.modbus_api.write_value("load_ball", True)
                self.modbus_api.write_value("load_ball", False)
            # reset previous state
            # if self.previous_state != 'attract':
            #     self.previous_state = 'attract'
            
        # elif self.state == "launch":
            # if self.modbus_api.read_value("shooter_lane_switch") == 0:
                # print("Launching ball")
                # self.sound_api.play("launch_ball")
                # self.modbus_api.write_value("launch_ball", True)
                # self.modbus_api.write_value("launch_ball", False)
                # self.state = "play"
                # self.previous_state = 'launch'
                # self.sound_api.set_background_music("pinball_wizard.wav", volume=0.5)

        # play state
        elif self.state == "play":
            self.current_ball = self.modbus_api.read_value('ball_drain')
            
            print(f"Current ball: {self.current_ball}")
            print(f"Active balls: {self.active_balls}")
            
            if pygame.mixer.music.get_busy() is False:
                self.sound_api.set_background_music("pinball_wizard.wav", volume=0.5)
            
            if self.previous_state == 'game_over' or self.previous_state == 'attract':
                #self.sound_api.set_background_music("pinball_wizard.wav", volume=0.5)
                self.previous_state = 'play'
                self.score = 0
                # self.modbus_api.write_value("drop_target_reset", True)
                
            
            # if self.current_ball < self.num_balls and self.active_balls == 0:
            #     print("Loading ball")
            #     # self.current_ball += 1    
            #     # print(f"Ball {self.current_ball}")
            #     self.active_balls += 1
            
            # check if event is ball_drain and lose condition
            if event_name == "ball_drain_pressed":
                print("Ball drained")
                self.sound_api.play("ball_drain")
                if self.current_ball < self.num_balls:
                    self.active_balls = 0
                    self.modbus_api.write_value("load_ball", True)
                    self.modbus_api.write_value("load_ball", False)
                    # self.active_balls -= 1
                else:
                    print("Game Over")
                    self.sound_api.stop_background_music()
                    self.state = "game_over"
                    self.previous_state = 'play'
                    self.game_over_elapsed_time = 0
                    self.active_balls = 0
                    # self.sound_api.set_background_music("fight_song.wav", volume=0.5)
                    self.modbus_api.write_value("game_over_bit", True)
                    # time.sleep(10)nj
                    
            # if self.previous_state == 'attract':
            #     self.previous_state = 'play'

        # game over state
        elif self.state == "game_over":
            # print("Checking for high score")
            # if self.high_scores.is_high_score(self.score):
            #     print(f"[HighScore] New high score: {self.score}")
            #     self.awaiting_high_score = True

            if self.previous_state == 'play' or self.previous_state == 'attract':
                self.sound_api.set_background_music("fight_song.wav", volume=0.5)
                self.previous_state = 'game_over'
                
            # self.sound_api.set_background_music("fight_song.wav", volume=1.0)
            if event_name == "start_button_pressed":
                print("Restarting game")
                self.last_score = self.score
                # self.score = 0
                self.state = "play"
                self.previous_state = 'game_over'

            elif event_name == "game_over_timeout":
                print("Transitioning to attract state")
                self.state = "attract"
                self.previous_state = 'game_over'

            # if self.state == "attract" or self.state == "play":
            #     self.score = 0
            #     self.game_over_elapsed_time = 0

    def update(self, delta_time: int):
        if self.awaiting_high_score:
            player_name = self.screen_api.get_player_name(self.score)
            self.high_scores.add_score(self.last_score, name=player_name)
            print(f"[HighScore] Saved: {player_name} - {self.score}")
            self.awaiting_high_score = False
            
        if self.state == "game_over" and not self.awaiting_high_score:
            if self.high_scores.is_high_score(self.score):
                print(f"[HighScore] New high score: {self.score}")
                self.awaiting_high_score = True
                return

        # print("[GameStateController] reading all values")
        all_values = self.modbus_api.read_all()

        # Check for low start_button coil
        # print("[GameStateController] Checking start button")
        start_button_val = all_values.get("start_button", 1)  # assume 1 if missing
        if self.state == "play":
            if self.previous_state == "attract" or self.previous_state == "game_over":
                self.sound_api.set_background_music("pinball_wizard.wav", volume=0.5)
                self.previous_state = "play"
            self.update_score()

            if start_button_val == 0:
                # print("[GameStateController] Start button released — returning to attract mode")
                self.state = "game_over"
                self.previous_state = "play"
                # self.score = 0
                # self.current_ball = 1
                self.game_over_elapsed_time = 0
            # return  # skip further updates this tick
        
        elif self.state == "game_over":
            self.game_over_elapsed_time += delta_time
            if self.previous_state == "play":
                self.sound_api.set_background_music("fight_song.wav", volume=0.5)
                self.previous_state = "game_over"

            if self.game_over_elapsed_time > 10000:
                print("[GameStateController] Game over timeout reached — returning to attract mode")
                self.last_score = self.score
                self.state = "attract"
                self.previous_state = "game_over"
                # self.score = 0
                # self.current_ball = 1
                self.game_over_elapsed_time = 0

    def update_score(self):
        total = 0
        all_values = self.modbus_api.read_all()
        for name, device in self.modbus_api.devices.items():
            if device.direction == "input" and device.reg_type in ("input_register", "holding_register") and device.score > 0:
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
    
    def get_ball_launch(self):
        val = self.modbus_api.read_value("shooter_lane_switch")
        if val == 0:
            return True
        else:
            return False
        
    
