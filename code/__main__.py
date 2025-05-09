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

print("Working directory:", os.getcwd())

# Add the directory of this file's parent (i.e. ~/projects/pinball) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from core.pinball_screen import PinballScreenAPI
from core.game_state import GameStateController
from core.modbus_api import ModbusClientAPI
from core.sound_manager import SoundManager

# from core.modbus_api import ModbusClientAPI
from core.event_system import GameEventSystem
from core.game_state import GameStateController
import time

plc_ip = "192.168.1.10"

config_path = os.path.join(os.path.dirname(__file__), "config/devices.json")
api = ModbusClientAPI(plc_ip, 502, config_path)
# api = ModbusClientAPI("localhost", 502, "config/devices.json")
events = GameEventSystem(api)
screen_api = PinballScreenAPI()

sound_mgr = SoundManager()

sound_mgr.load_sound("fight_song", "fight_song.mp3")
sound_mgr.load_sound("awakening", "awakening.mp3")
sound_mgr.load_sound("chaching", "chaching.mp3")

controller = GameStateController(
    screen_api=screen_api,
    sound_manager=sound_mgr,
    event_system=events,
    modbus_api=api,
)


for name in api.devices.keys():
    events.register(f"{name}_pressed", lambda n=name: controller.handle_event(f"{n}_pressed"))
# Register relevant events
# events.register("start_button_pressed", lambda: controller.handle_event("start_button_pressed"))
# events.register("ball_trough_pressed", lambda: controller.handle_event("ball_trough_pressed"))
events.register("game_over_timeout", lambda: controller.handle_event("game_over_timeout"))

clock = pygame.time.Clock()
running = True

try:
    while running:
        # print("State:", controller.get_state())
        # print("Score:", controller.score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        # time.sleep(0.5)

        delta_time = clock.get_time()
        controller.update(delta_time)
        screen_api.update(state=controller.get_state(), score=controller.get_score(), ball=controller.get_ball())
        clock.tick(30)
finally:
    events.stop()
    api.stop()
    pygame.quit()
