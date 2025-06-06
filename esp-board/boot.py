
"""
ESP32 IoT Control System - Safe Boot Module
===========================================

A robust boot script for ESP32 IoT control system that provides safe mode functionality
and graceful startup/shutdown procedures. This module ensures system stability and
provides debugging capabilities through safe mode operations.

Author: Erfan Mohamadnia
License: MIT
Version: 1.0.0

Features:
- Safe mode detection and activation
- User interrupt handling during startup
- Recovery tools for system debugging
- Automatic/manual startup options
- Persian/English bilingual support

Hardware Requirements:
- ESP32 development board
- BOOT button (GPIO0) for hardware safe mode trigger

Usage:
    This script runs automatically on ESP32 boot. Users can:
    - Press Ctrl+C during 10-second startup window for safe mode
    - Hold BOOT button and press RESET for hardware safe mode
    - Create 'safe_mode.txt' file with content '1' for persistent safe mode
"""

import sys
import gc
import time
from machine import Pin, reset, Timer

def check_safe_mode():
    """
    Check if safe mode is requested through file or hardware button.
    
    Safe mode can be activated through:
    1. Creating a 'safe_mode.txt' file with content '1'
    2. Pressing the BOOT button (GPIO0) during startup
    
    Returns:
        bool: True if safe mode should be activated, False otherwise
    """
    
    # Check for safe mode file
    try:
        with open('safe_mode.txt', 'r') as f:
            content = f.read().strip()
            if content == '1':
                print("🔒 Safe mode enabled - حالت ایمن فعال")
                return True
    except OSError:
        # File doesn't exist, continue with normal checks
        pass
    
    # Check GPIO0 button (BOOT button) for hardware safe mode trigger
    try:
        boot_pin = Pin(0, Pin.IN, Pin.PULL_UP)
        if not boot_pin.value():  # Button pressed (active low)
            print("🔒 Safe mode: BOOT button pressed")
            print("🔒 حالت ایمن: دکمه BOOT فشرده شده")
            return True
    except Exception:
        # GPIO initialization failed, continue without hardware check
        pass
    
    return False

def wait_for_interrupt():
    """
    Wait for user interrupt during startup countdown.
    
    Provides a 10-second window for users to enter safe mode by pressing Ctrl+C.
    Displays bilingual messages (English/Persian) to guide users.
    
    Returns:
        bool: True if user interrupted startup, False if countdown completed
    """
    
    print("\n" + "="*50)
    print("🚀 ESP32 IoT Control System Starting...")
    print("🚀 سیستم کنترل IoT ESP32 در حال شروع...")
    print("="*50)
    
    print("\n⚠️  IMPORTANT / مهم:")
    print("   Press Ctrl+C within 10 seconds to enter safe mode")
    print("   برای ورود به حالت ایمن، Ctrl+C را ظرف 10 ثانیه فشار دهید")
    print("   Or hold BOOT button and press RESET")
    print("   یا دکمه BOOT را نگه دارید و RESET را فشار دهید")
    
    for i in range(10, 0, -1):
        try:
            print(f"\r⏱️  Starting in {i} seconds... (Ctrl+C to stop)", end="")
            print(f" / شروع در {i} ثانیه... (Ctrl+C برای توقف)", end="")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🔒 Safe mode activated by user interrupt")
            print("🔒 حالت ایمن توسط کاربر فعال شد")
            return True
    
    print("\n\n✅ Starting normal operation...")
    print("✅ شروع عملکرد عادی...")
    return False

def create_safe_mode_tools():
    """
    Create interactive tools and helper functions for safe mode operation.
    
    This function creates a set of utility functions that become available
    in the REPL when safe mode is activated. These tools help users:
    - Manage auto-start settings
    - Manually start the IoT system
    - Check system files
    - Control boot behavior
    
    Available Functions:
        enable_auto_start(): Enable automatic system startup on next boot
        disable_auto_start(): Keep system in safe mode on next boot
        start_system(): Manually start the IoT control system
        check_files(): List all files in the root directory
        reset(): Restart the ESP32
    """
    
    print("\n🛠️  Safe Mode Tools Available:")
    print("🛠️  ابزارهای حالت ایمن موجود:")
    print("   - Edit files using REPL")
    print("   - ویرایش فایل‌ها با استفاده از REPL")
    print("   - Check system status")
    print("   - بررسی وضعیت سیستم")
    print("   - Manual WiFi connection")
    print("   - اتصال دستی وایفای")
    
    # Create helper functions for safe mode operations
    def enable_auto_start():
        """Enable auto-start for next boot by setting safe_mode flag to 0."""
        try:
            with open('safe_mode.txt', 'w') as f:
                f.write('0')
            print("✅ Auto-start enabled for next boot")
            print("✅ شروع خودکار برای بوت بعدی فعال شد")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def disable_auto_start():
        """Disable auto-start (maintain safe mode) by setting safe_mode flag to 1."""
        try:
            with open('safe_mode.txt', 'w') as f:
                f.write('1')
            print("🔒 Auto-start disabled (safe mode)")
            print("🔒 شروع خودکار غیرفعال شد (حالت ایمن)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def start_system():
        """Manually start the IoT system from safe mode."""
        try:
            print("🚀 Starting IoT system manually...")
            print("🚀 شروع دستی سیستم IoT...")
            from main_board import ESP32Controller
            controller = ESP32Controller()
            controller.run()
        except Exception as e:
            print(f"❌ Error starting system: {e}")
            print(f"❌ خطا در شروع سیستم: {e}")
    
    def check_files():
        """List all available files in the root directory."""
        import os
        try:
            files = os.listdir('/')
            print("📁 Available files:")
            print("📁 فایل‌های موجود:")
            for file in files:
                print(f"   - {file}")
        except Exception as e:
            print(f"❌ Error listing files: {e}")
    
    # Make functions available globally
    globals()['enable_auto_start'] = enable_auto_start
    globals()['disable_auto_start'] = disable_auto_start
    globals()['start_system'] = start_system
    globals()['check_files'] = check_files
    
    print("\n📋 Available commands:")
    print("📋 دستورات موجود:")
    print("   enable_auto_start()  - Enable auto-start")
    print("   disable_auto_start() - Keep safe mode")
    print("   start_system()       - Start IoT system")
    print("   check_files()        - List files")
    print("   reset()              - Restart ESP32")

def boot_system():
    """
    Initialize and start the ESP32 IoT Control System.
    
    This function performs the complete system startup sequence:
    1. Load and validate configuration
    2. Initialize the main controller
    3. Start the IoT control system
    4. Handle any startup errors gracefully
    
    Returns:
        bool: True if system started successfully, False on error
    
    Raises:
        Exception: Re-raises any critical errors that prevent system startup
    """
    
    print("="*50)
    print("🚀 Starting ESP32 IoT Control System")
    print("🚀 شروع سیستم کنترل IoT ESP32")
    print("="*50)
    
    # Import and validate system configuration
    try:
        import config
        print("✅ Configuration loaded")
        print("✅ پیکربندی بارگذاری شد")
    except Exception as e:
        print(f"❌ Config error: {e}")
        print(f"❌ خطای پیکربندی: {e}")
        return False
    
    # Initialize and start the main controller
    try:
        print("🚀 Initializing controller...")
        print("🚀 راه‌اندازی کنترل‌کننده...")
        
        from main_board import ESP32Controller
        controller = ESP32Controller()
        
        # Perform garbage collection to free memory before starting
        gc.collect()
        print(f"📊 Free Memory: {gc.mem_free()} bytes")
        print(f"📊 حافظه آزاد: {gc.mem_free()} بایت")
        
        # Start the IoT control system
        controller.run()
        
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
        print("\n🛑 سیستم توسط کاربر متوقف شد")
        return False
        
    except Exception as e:
        print(f"❌ System error: {e}")
        print(f"❌ خطای سیستم: {e}")
        return False
    
    return True

# ============================================================================
# Main Boot Execution
# ============================================================================

try:
    # Perform initial garbage collection to free memory
    gc.collect()
    
    # Check for safe mode activation
    if check_safe_mode():
        print("\n🔒 SAFE MODE ACTIVE")
        create_safe_mode_tools()
        
    else:
        # Check for user interrupt during startup countdown
        if wait_for_interrupt():
            print("\n🔒 ENTERING SAFE MODE")
            print("🔒 ورود به حالت ایمن")
            create_safe_mode_tools()
        else:
            # Proceed with normal system boot
            boot_system()

except Exception as e:
    # Handle any critical boot errors by entering safe mode
    print(f"❌ Boot error: {e}")
    print(f"❌ خطای بوت: {e}")
    print("🔒 Entering safe mode...")
    print("🔒 ورود به حالت ایمن...")
    create_safe_mode_tools()
