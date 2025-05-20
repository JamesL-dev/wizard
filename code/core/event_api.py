"""
Game Event System
=================

This module defines the Game Event system.

Author: Kevin Wing
Project: University of Idaho PLC Pinball
Last Updated: 3/7/2025
"""

import threading
import time
from core.modbus_api import ModbusAPI

class EventAPI:
    """
    Monitors Modbus inputs for changes and emits events on rising edges or value changes.
    Allows registering callbacks for specific events.
    """
    def __init__(self, modbus_api: ModbusAPI):
        self.api = modbus_api
        self.callbacks = {}
        self.last_values = {}
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def register(self, event_name: str, callback):
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)

    def _emit(self, event_name: str):
        for callback in self.callbacks.get(event_name, []):
            callback()
    
    def emit(self, event_name: str):
        """Emit custom event"""
        print(f"[GameEventSystem] Emitting Event {event_name}")
        self._emit(event_name)

    def _monitor_loop(self):
        while self.running:
            current_values = self.api.read_all()
            for name, current in current_values.items():
                last = self.last_values.get(name, 0)
                # if current == 1 and last == 0:
                #     self._emit(f"{name}_pressed")
                if current != last:
                    self._emit(f"{name}_pressed")
                elif current != last:
                    self._emit(f"{name}_changed")
                self.last_values[name] = current
            time.sleep(0.05)

    def stop(self):
        self.running = False
        self.thread.join()
