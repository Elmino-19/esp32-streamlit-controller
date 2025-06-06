"""
Servo Controller Module for ESP32 IoT Control System
==================================================

Provides servo motor control through PCA9685 I2C PWM driver for precise
angular positioning. Supports standard servo motors with configurable
pulse width parameters and angle limits.

Author: Erfan Mohamadnia
License: MIT
Version: 1.0.0

Features:
- PCA9685 I2C PWM driver integration
- Configurable pulse width parameters (500-2500μs)
- 0-180 degree angle control with safety limits
- Automatic duty cycle calculation
- Standard 50Hz PWM frequency for servo compatibility

Hardware Requirements:
- ESP32 development board with I2C capability
- PCA9685 16-channel PWM driver board
- Standard servo motor (SG90, MG996R, etc.)
- Proper power supply for servo motor

Connection:
- ESP32 SDA -> PCA9685 SDA
- ESP32 SCL -> PCA9685 SCL
- Servo signal -> PCA9685 channel output
- Servo power -> External 5V/6V supply
"""

from machine import I2C, Pin
import time


class PCA9685:
    """
    PCA9685 16-channel PWM driver controller.
    
    Provides low-level interface to PCA9685 I2C PWM driver chip for generating
    precise PWM signals required for servo motor control. Handles I2C communication
    and PWM frequency configuration.
    """
    
    def __init__(self, i2c, address=0x40):
        """
        Initialize PCA9685 PWM driver.
        
        Args:
            i2c: I2C bus object for communication
            address (int): I2C slave address (default: 0x40)
        """
        self.i2c = i2c
        self.address = address
        self.set_pwm_freq(50)  # Standard frequency for servo motors

    def write8(self, reg, value):
        """Write 8-bit value to PCA9685 register."""
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def set_pwm_freq(self, freq_hz):
        """
        Set PWM frequency for all channels.
        
        Args:
            freq_hz (int): PWM frequency in Hz (typically 50 for servos)
        """
        # Calculate prescaler value for desired frequency
        prescale_val = int(25000000.0 / (4096 * freq_hz) - 1)
        
        # Enter sleep mode to change prescaler
        self.write8(0x00, 0x10)  # Sleep mode
        self.write8(0xFE, prescale_val)  # Set prescaler
        self.write8(0x00, 0x00)  # Normal mode
        time.sleep_ms(1)
        self.write8(0x00, 0xa1)  # Restart and enable auto-increment

    def set_pwm(self, channel, on, off):
        """
        Set PWM values for specific channel.
        
        Args:
            channel (int): PWM channel (0-15)
            on (int): Turn-on time (0-4095)
            off (int): Turn-off time (0-4095)
        """
        base_reg = 0x06 + 4 * channel
        self.i2c.writeto_mem(self.address, base_reg, bytes([on & 0xFF]))
        self.i2c.writeto_mem(self.address, base_reg + 1, bytes([on >> 8]))
        self.i2c.writeto_mem(self.address, base_reg + 2, bytes([off & 0xFF]))
        self.i2c.writeto_mem(self.address, base_reg + 3, bytes([off >> 8]))


class ServoController:
    """
    High-level servo motor controller using PCA9685.
    
    Provides simple angle-based control for servo motors by converting
    angle values to appropriate PWM duty cycles. Handles pulse width
    calculations and safety limits automatically.
    """
    
    def __init__(self, i2c_scl=22, i2c_sda=21, channel=0, min_us=500, max_us=2500, freq=50):
        """
        Initialize servo controller with I2C and servo parameters.
        
        Args:
            i2c_scl (int): I2C SCL pin number (default: 22)
            i2c_sda (int): I2C SDA pin number (default: 21)
            channel (int): PCA9685 channel for servo (default: 0)
            min_us (int): Minimum pulse width in microseconds (default: 500)
            max_us (int): Maximum pulse width in microseconds (default: 2500)
            freq (int): PWM frequency in Hz (default: 50)
        """
        # Initialize I2C bus
        self.i2c = I2C(0, scl=Pin(i2c_scl), sda=Pin(i2c_sda))
        
        # Initialize PCA9685 driver
        self.pca = PCA9685(self.i2c)
        
        # Store servo parameters
        self.channel = channel
        self.freq = freq
        self.min_duty = self.us_to_duty(min_us)
        self.max_duty = self.us_to_duty(max_us)

    def us_to_duty(self, us):
        """
        Convert microseconds to PWM duty cycle value.
        
        Args:
            us (int): Pulse width in microseconds
            
        Returns:
            int: Duty cycle value (0-4095)
        """
        period = 1000000 // self.freq  # Period in microseconds
        duty = int(us * 4096 // period)
        return duty

    def angle_to_duty(self, angle):
        """
        Convert servo angle to PWM duty cycle.
        
        Maps input angle (0-180°) to appropriate duty cycle value
        based on configured pulse width limits.
        
        Args:
            angle (float): Servo angle in degrees (0-180)
            
        Returns:
            int: Duty cycle value for PCA9685
        """
        # Clamp angle to valid range
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
            
        # Linear interpolation between min and max duty cycles
        duty_range = self.max_duty - self.min_duty
        duty = int(self.min_duty + (angle / 180) * duty_range)
        return duty

    def set_angle(self, angle):
        """
        Set servo to specified angle.
        
        Args:
            angle (float): Target angle in degrees (0-180)
        """
        duty = self.angle_to_duty(angle)
        self.pca.set_pwm(self.channel, 0, duty)
        print(f"🎯 Servo positioned at {angle}° (duty: {duty})")
        print(f"🎯 سروو روی زاویه {angle} درجه تنظیم شد")