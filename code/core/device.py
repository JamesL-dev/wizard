"""
Device Module
==========

This module defines the Device class for creating pinball hardware devices.

Author: Kevin Wing
Project: University of Idaho PLC Pinball
Last Updated: 3/6/2025
"""

class Device:
    """
    Represents a Modbus device defined in the configuration.
    Each device has a name, address, register type, and direction.
    """
    def __init__(self, name: str, address: int, reg_type: str, direction: str, score: int):
        self.name = name
        self.address = address
        self.reg_type = reg_type
        self.direction = direction
        self.score = score
        self.starting_count = 0
