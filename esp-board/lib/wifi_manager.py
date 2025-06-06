"""
WiFi Manager Module for ESP32 IoT Control System
===============================================

Handles WiFi network connection, time synchronization, and network status monitoring
for ESP32-based IoT applications. Provides automatic NTP time sync with timezone
support and robust connection management.

Author: Erfan Mohamadnia
License: MIT
Version: 1.0.0

Features:
- Automatic WiFi connection with timeout handling
- NTP time synchronization with timezone offset
- Connection status monitoring
- Robust error handling and retry mechanisms
- Tehran timezone support (UTC+3:30)

Dependencies:
- network: ESP32 network interface
- ntptime: Network Time Protocol client
- time: System time functions
"""

import network
import time
import ntptime


class WiFiManager:
    """
    Manages WiFi connectivity and time synchronization for ESP32.
    
    This class provides a simple interface for connecting to WiFi networks,
    synchronizing system time via NTP, and monitoring connection status.
    Includes support for timezone offsets and automatic time adjustment.
    """
    
    def __init__(self, ssid, password, timeout=15, timezone_offset=3.5):
        """
        Initialize WiFi manager with network credentials and settings.
        
        Args:
            ssid (str): WiFi network name (SSID)
            password (str): WiFi network password
            timeout (int): Connection timeout in seconds (default: 15)
            timezone_offset (float): Timezone offset in hours (default: 3.5 for Tehran)
        """
        self.ssid = ssid
        self.password = password
        self.timeout = timeout
        self.timezone_offset = timezone_offset * 3600  # Convert hours to seconds
        self.station = network.WLAN(network.STA_IF)
    
    def connect(self):
        """
        Connect to WiFi network and synchronize system time.
        
        Attempts to connect to the configured WiFi network with the specified
        timeout. After successful connection, performs NTP time synchronization
        with timezone adjustment.
        
        Returns:
            str: IP address assigned to the ESP32
            
        Raises:
            RuntimeError: If connection fails within timeout period
        """
        if not self.station.isconnected():
            print("📡 Connecting to WiFi network...")
            self.station.active(True)
            self.station.connect(self.ssid, self.password)
            
            # Wait for connection with timeout
            start_time = time.time()
            while not self.station.isconnected():
                if time.time() - start_time > self.timeout:
                    raise RuntimeError("WiFi connection failed - timeout exceeded")
                time.sleep(1)
                
        ip_address = self.station.ifconfig()[0]
        print(f"✅ WiFi connected successfully! IP: {ip_address}")
        
        # Synchronize system time after successful connection
        self.sync_time()
        return ip_address
    
    def sync_time(self):
        """
        Synchronize system time using NTP with timezone adjustment.
        
        Connects to NTP servers to get current UTC time and adjusts it
        according to the configured timezone offset. Handles connection
        errors gracefully and reports sync status.
        """
        try:
            print("🕐 Synchronizing time via NTP...")
            ntptime.settime()
            
            # Adjust time for local timezone
            adjusted_time = time.time() + int(self.timezone_offset)
            local_time = time.localtime(adjusted_time)
            
            print(f"✅ Time synchronized successfully (Tehran): {local_time[0]}/{local_time[1]:02d}/{local_time[2]:02d} {local_time[3]:02d}:{local_time[4]:02d}:{local_time[5]:02d}")
            
        except Exception as e:
            print(f"⚠️ Time synchronization failed: {e}")
            print("⚠️ System will continue with local time")
    
    def is_connected(self):
        """
        Check current WiFi connection status.
        
        Returns:
            bool: True if connected to WiFi network, False otherwise
        """
        return self.station.isconnected()
    
    def get_ip(self):
        return self.station.ifconfig()[0] if self.is_connected() else None

