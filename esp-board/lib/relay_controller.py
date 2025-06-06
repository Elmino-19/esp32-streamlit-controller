"""
Relay Controller Module for ESP32 IoT Control System
==================================================

Provides GPIO-based relay control for managing pumps, motors, and other
electrical devices through ESP32 digital outputs. Supports multiple relay
channels with individual and group control capabilities.

Author: Erfan Mohamadnia
License: MIT
Version: 1.0.0

Features:
- Multi-channel relay control via GPIO pins
- Individual relay on/off control
- Group operations (all on/all off)
- Active-low relay logic support
- Safe initialization with all relays off

Hardware Requirements:
- ESP32 development board
- Relay module(s) with optocoupler isolation
- Proper power supply for connected devices

Usage Example:
    relay_pins = [14, 25, 26, 27]  # GPIO pins for 4 relays
    controller = RelayController(relay_pins)
    controller.on(0)    # Turn on relay 0
    controller.off(1)   # Turn off relay 1
    controller.off_all() # Turn off all relays
"""

from machine import Pin


class RelayController:
    """
    Controls multiple relay channels through ESP32 GPIO pins.
    
    This class manages a collection of relays connected to ESP32 GPIO pins,
    providing methods for individual and group control. Assumes active-low
    relay logic where LOW signal activates the relay.
    
    Attributes:
        relays (list): List of Pin objects for relay control
    """
    
    def __init__(self, pins):
        """
        Initialize relay controller with specified GPIO pins.
        
        Creates Pin objects for each specified GPIO pin and sets them as
        outputs. All relays are initialized to OFF state (HIGH signal)
        for safety.
        
        Args:
            pins (list): List of GPIO pin numbers for relay control
        """
        self.relays = [Pin(pin, Pin.OUT) for pin in pins]
        
        # Initialize all relays to OFF state (active-low logic)
        for relay in self.relays:
            relay.value(1)  # HIGH = OFF for active-low relays
    
    def on(self, channel):
        """
        Turn on a specific relay channel.
        
        Args:
            channel (int): Relay channel number (0-based index)
        """
        if 0 <= channel < len(self.relays):
            self.relays[channel].value(0)  # LOW = ON for active-low relays
    
    def off(self, channel):
        """
        Turn off a specific relay channel.
        
        Args:
            channel (int): Relay channel number (0-based index)
        """
        if 0 <= channel < len(self.relays):
            self.relays[channel].value(1)  # HIGH = OFF for active-low relays
    
    def off_all(self):
        """Turn off all relay channels simultaneously."""
        for relay in self.relays:
            relay.value(1)  # HIGH = OFF for active-low relays
    
    def on_all(self):
        """Turn on all relay channels simultaneously."""
        for relay in self.relays:
            relay.value(0)  # LOW = ON for active-low relays
