"""
__main__.py
==========

This file serves as the entry point to the game. To run the game:

python -m pinball

Author: Kevin Wing
Project: University of Idaho PLC Pinball
Last Updated: 3/11/2025
"""
import sys
import os
import pygame
# import time

print("Working directory:", os.getcwd())

# Add the directory of this file's parent (i.e. ~/projects/pinball) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Import the necessary APIs
from core.screen_api import ScreenAPI
from core.modbus_api import ModbusAPI
from core.sound_api import SoundAPI
from core.event_api import EventAPI

# import the GameStateController class
from core.game_state import GameStateController

plc_modbus_ip = "192.168.1.10"
plc_modbus_port = 502

config_path = os.path.join(os.path.dirname(__file__), "config/devices.json")
sound_path = os.path.join(os.path.dirname(__file__), "assets/sounds")

modbus_api = ModbusAPI(plc_modbus_ip, plc_modbus_port, config_path)
event_api = EventAPI(modbus_api)
screen_api = ScreenAPI()
sound_api = SoundAPI(sound_dir=sound_path)

# Load sounds
# sound_api.load_sound("fight_song", "fight_song.mp3")
# sound_api.load_sound("awakening", "awakening.mp3")
sound_api.load_sound("chaching", "chaching.mp3")
sound_api.load_sound("ball_drain", "ball_drain.wav")

controller = GameStateController(
    screen_api=screen_api,
    sound_api=sound_api,
    event_api=event_api,
    modbus_api=modbus_api,
)

# Register events for all devices
for name in modbus_api.devices.keys():
    print(f"[DEBUG] Registering event for device: {name}")
    event_api.register(f"{name}_pressed", lambda n=name: controller.handle_event(f"{n}_pressed"))

# Register specific events
print("[DEBUG] Registering specific events")
event_api.register("game_over_timeout", lambda: controller.handle_event("game_over_timeout"))

clock = pygame.time.Clock()
running = True

try:
    print("[DEBUG] Starting main loop")
    while running:
        # print("State:", controller.get_state())
        # print("Score:", controller.score)
        # print(f"[DEBUG] Current state: {controller.state}")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("[DEBUG] Quitting game")
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("[DEBUG] Quitting game")
                running = False
        # time.sleep(0.5)

        # print(f"[DEBUG] getting delta time")
        delta_time = clock.get_time()
        
        # print(f"[DEBUG] Updating controller with delta time: {delta_time}")
        controller.update(delta_time)
        # print(f"[DEBUG] Updating screen API")
        screen_api.update(
            state=controller.get_state(),
            score=controller.get_score(),
            ball=controller.get_ball(),
            ball_launch=controller.get_ball_launch(),
            high_scores=controller.high_scores.get_scores(),
            last_score=controller.last_score,
        )
        
        clock.tick(30)
finally:
    # stop the API threads
    event_api.stop()
    modbus_api.stop()
    pygame.quit()
