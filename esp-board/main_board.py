"""
ESP32 IoT Control System - Main Application Controller
====================================================

The main application module that orchestrates the entire ESP32 IoT control system.
This module integrates WiFi connectivity, hardware control, task scheduling, and
web server functionality into a cohesive IoT solution.

Author: Erfan Mohamadnia
License: MIT
Version: 1.0.0

Features:
- Asynchronous web server with REST API
- Multi-device control (pumps, DC motor, servo)
- Task scheduling and automation
- WiFi network management with NTP time sync
- Graceful error handling and system recovery
- Memory management and optimization
- Bilingual support (English/Persian)

Hardware Support:
- 4-channel relay control for pumps and DC motor
- PCA9685-based servo control via I2C
- ESP32 development board with WiFi capability

Dependencies:
- uasyncio: Asynchronous I/O operations
- machine: Hardware abstraction layer
- ujson: JSON parsing and generation
- Custom modules: WiFiManager, RelayController, ServoController, TaskManager, WebServer
"""

import time
import uasyncio as asyncio
from machine import Pin, I2C, RTC, Timer
import gc
import ujson as json

# Import system configuration and custom modules
import config
from lib.wifi_manager import WiFiManager
from lib.relay_controller import RelayController
from lib.servo_controler import ServoController
from lib.task_manager import TaskManager
from lib.web_server import WebServer

class ESP32Controller:
    """
    Main controller class for ESP32 IoT Control System.
    
    This class serves as the central coordinator for all system components,
    managing hardware initialization, network connectivity, task scheduling,
    and web server operations. It provides a unified interface for controlling
    multiple devices and handling system-wide operations.
    
    Attributes:
        config: System configuration object
        wifi_manager: WiFi connection and time synchronization handler
        relay_controller: 4-channel relay control for pumps and DC motor
        servo_controller: PCA9685-based servo motor controller
        task_manager: Scheduled task management system
        web_server: Asynchronous HTTP server for REST API
        rtc: Real-time clock for system timing
        device_status: Current state tracking for all devices
        auto_off_timers: Timer objects for automatic device shutdown
    """
    
    def __init__(self):
        """Initialize the ESP32 controller with default settings and component references."""
        print("🚀 Starting ESP32 IoT Control System...")
        print("🚀 راه‌اندازی سیستم کنترل IoT با ESP32...")
        
        # Load system configuration
        self.config = config
        
        # Extract WiFi settings from configuration
        self.wifi_config = self.config.WIFI_CONFIG
        
        # Initialize component references (will be set during initialization)
        self.wifi_manager = None
        self.relay_controller = None
        self.servo_controller = None
        self.task_manager = None
        self.web_server = None
        self.rtc = RTC()
        
        # Task scheduler timer for periodic task checking
        self.task_timer = Timer(0)
        
        # Device status tracking dictionary
        self.device_status = {
            device: False for device in self.config.DEVICE_CONFIG.keys() 
            if device != 'servo'
        }
        self.device_status['servo'] = self.config.DEFAULTS['servo_angle']  # Store servo angle
        
        # Timer objects for automatic device shutdown
        self.auto_off_timers = {}
        
    def initialize_hardware(self):
        """
        Initialize all hardware components and controllers.
        
        This method sets up the relay controller for pump and motor control,
        initializes the servo controller with PCA9685 driver, and creates
        the task manager for scheduled operations.
        
        Raises:
            Exception: If any hardware component fails to initialize
        """
        try:
            print("🔧 Initializing hardware components...")
            print("🔧 مقداردهی اولیه اجزای سخت‌افزاری...")
            
            # Initialize 4-channel relay controller for pumps and DC motor
            relay_pins = self.config.HARDWARE_CONFIG['relay_pins']
            self.relay_controller = RelayController(relay_pins)
            print("✅ Relay controller initialized - کنترل‌کننده رله مقداردهی شد")
            
            # Initialize servo controller with PCA9685 I2C driver
            servo_config = self.config.HARDWARE_CONFIG['servo_config']
            i2c_config = self.config.HARDWARE_CONFIG['i2c_config']
            
            self.servo_controller = ServoController(
                i2c_scl=i2c_config['scl_pin'],
                i2c_sda=i2c_config['sda_pin'],
                channel=servo_config['channel'],
                min_us=servo_config['min_pulse_us'],
                max_us=servo_config['max_pulse_us'],
                freq=servo_config['frequency']
            )
            print("✅ Servo controller initialized - کنترل‌کننده سروو مقداردهی شد")
            
            # Initialize task manager for scheduled operations
            task_config = self.config.TASK_CONFIG
            self.task_manager = TaskManager(
                filename=task_config['filename'], 
                max_tasks=task_config['max_tasks']
            )
            print("✅ Task manager initialized - مدیر تسک مقداردهی شد")
            
        except Exception as e:
            print(f"❌ Hardware initialization error: {e}")
            print(f"❌ خطا در مقداردهی سخت‌افزار: {e}")
            raise
    
    def connect_wifi(self):
        """
        Establish WiFi connection and synchronize system time.
        
        Uses the WiFiManager to connect to the configured network and
        perform NTP time synchronization. Displays connection status
        and current time after successful connection.
        
        Returns:
            str: Assigned IP address
            
        Raises:
            Exception: If WiFi connection or time sync fails
        """
        try:
            print("📡 Connecting to WiFi...")
            print("📡 اتصال به WiFi...")
            
            self.wifi_manager = WiFiManager(
                ssid=self.wifi_config['ssid'],
                password=self.wifi_config['password'],
                timeout=self.wifi_config['timeout'],
                timezone_offset=self.wifi_config['timezone_offset']
            )
            
            ip = self.wifi_manager.connect()
            print(f"✅ Connected to WiFi! IP: {ip}")
            print(f"✅ به WiFi متصل شد! آی‌پی: {ip}")
            
            # Display current synchronized time
            current_time = time.localtime()
            print(f"🕐 Current time: {current_time[0]}/{current_time[1]:02d}/{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}")
            print(f"🕐 زمان فعلی: {current_time[0]}/{current_time[1]:02d}/{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}")
            
            return ip
            
        except Exception as e:
            print(f"❌ WiFi connection error: {e}")
            print(f"❌ خطا در اتصال WiFi: {e}")
            raise
    
    def setup_web_server(self):
        """
        Configure and initialize the asynchronous web server.
        
        Creates a WebServer instance with relay and servo controller
        references for device control API endpoints. Prepares the
        server for handling HTTP requests asynchronously.
        
        Raises:
            Exception: If web server configuration fails
        """
        try:
            print("🌐 Setting up web server...")
            print("🌐 راه‌اندازی وب‌سرور...")
            
            # Initialize WebServer with relay and servo controllers
            self.web_server = WebServer(self.relay_controller, self.servo_controller)
            print("✅ Web server configured - وب‌سرور پیکربندی شد")
            
        except Exception as e:
            print(f"❌ Web server setup error: {e}")
            print(f"❌ خطا در راه‌اندازی وب‌سرور: {e}")
            raise
    
    def check_scheduled_tasks(self, timer):
        """
        Periodic callback function to check and execute scheduled tasks.
        
        This method is called by a timer every minute to check if any
        scheduled tasks should be executed. Compares current time with
        task schedule and executes matching tasks automatically.
        
        Args:
            timer: Timer object that triggered this callback (unused)
        """
        try:
            current_time = time.localtime()
            current_date = f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d}"
            current_time_str = f"{current_time[3]:02d}:{current_time[4]:02d}"
            
            tasks = self.task_manager.get_tasks()
            
            for i, task in enumerate(tasks):
                if task['date'] == current_date and task['time'] == current_time_str:
                    # Execute matching scheduled task
                    device = task['device']
                    duration = task['duration']
                    
                    print(f"⏰ Executing scheduled task: {device} for {duration}s")
                    print(f"⏰ اجرای تسک برنامه‌ریزی شده: {device} برای {duration} ثانیه")
                    
                    # Execute device-specific commands
                    if device == 'pump1':
                        self.relay_controller.on(0)
                        self.device_status['pump1'] = True
                        self._set_auto_off_timer('pump1', 0, duration)
                    elif device == 'pump2':
                        self.relay_controller.on(1)
                        self.device_status['pump2'] = True
                        self._set_auto_off_timer('pump2', 1, duration)
                    elif device == 'pump3':
                        self.relay_controller.on(2)
                        self.device_status['pump3'] = True
                        self._set_auto_off_timer('pump3', 2, duration)
                    elif device == 'dcmotor':
                        self.relay_controller.on(3)
                        self.device_status['dcmotor'] = True
                        self._set_auto_off_timer('dcmotor', 3, duration)
                    
                    # Remove executed task from schedule
                    self.task_manager.delete_task(i)
                    break  # Process one task per check to avoid index issues
                    
        except Exception as e:
            print(f"❌ Task execution error: {e}")
            print(f"❌ خطا در اجرای تسک: {e}")
    
    def _set_auto_off_timer(self, device_name, channel, duration):
        """
        Configure automatic shutdown timer for a specific device.
        
        Creates a one-shot timer that will automatically turn off the
        specified device after the given duration. Manages timer cleanup
        and device status updates upon completion.
        
        Args:
            device_name (str): Name identifier for the device
            channel (int): Hardware channel number for relay control
            duration (int): Time in seconds before automatic shutdown
        """
        def auto_off_callback(timer):
            self.relay_controller.off(channel)
            self.device_status[device_name] = False
            # Clean up timer reference
            if device_name in self.auto_off_timers:
                del self.auto_off_timers[device_name]
        
        # Cancel existing timer if device is already scheduled
        if device_name in self.auto_off_timers:
            self.auto_off_timers[device_name].deinit()
        
        # Create and configure new auto-off timer
        self.auto_off_timers[device_name] = Timer(-1)
        self.auto_off_timers[device_name].init(
            mode=Timer.ONE_SHOT,
            period=duration * 1000,  # Convert seconds to milliseconds
            callback=auto_off_callback
        )
    
    def start_task_scheduler(self):
        """
        Initialize and start the periodic task scheduler.
        
        Configures a timer that checks for scheduled tasks every minute
        and executes them automatically. The scheduler runs continuously
        in the background to enable automated device operations.
        """
        print("📅 Starting task scheduler...")
        print("📅 شروع برنامه‌ریز تسک...")
        
        # Configure timer to check scheduled tasks every minute
        self.task_timer.init(
            mode=Timer.PERIODIC,
            period=60000,  # 60 seconds interval
            callback=self.check_scheduled_tasks
        )
    
    async def run_async(self):
        """
        Main asynchronous execution method for the ESP32 controller.
        
        Orchestrates the complete system startup sequence including hardware
        initialization, network connection, web server setup, and task
        scheduling. Handles graceful shutdown on interruption or errors.
        
        Raises:
            KeyboardInterrupt: User-requested system shutdown
            Exception: Any system-level error during operation
        """
        try:
            print("🚀 ESP32 IoT Control System Starting...")
            print("🚀 سیستم کنترل IoT ESP32 در حال راه‌اندازی...")
            
            # Initialize hardware
            self.initialize_hardware()
            
            # Connect to WiFi
            ip = self.connect_wifi()
            
            # Setup web server
            self.setup_web_server()
            
            # Start task scheduler
            self.start_task_scheduler()
            
            # Start web server
            print("🌐 Starting async web server...")
            print("🌐 شروع وب‌سرور async...")
            print(f"🌍 Access your ESP32 at: http://{ip}")
            print(f"🌍 به ESP32 خود دسترسی پیدا کنید: http://{ip}")
            
            # Start the asynchronous web server
            await self.web_server.start(host='0.0.0.0', port=80)
            
        except KeyboardInterrupt:
            print("🛑 System shutdown requested...")
            print("🛑 درخواست خاموش کردن سیستم...")
            self.shutdown()
        except Exception as e:
            print(f"❌ System error: {e}")
            print(f"❌ خطای سیستم: {e}")
            self.shutdown()
    
    def run(self):
        """
        Main synchronous entry point for system execution.
        
        Starts the asynchronous event loop and handles top-level
        exceptions. Provides a simple interface for running the
        complete ESP32 IoT control system.
        
        Raises:
            Exception: Critical system errors that prevent startup
        """
        try:
            print("✅ ESP32 IoT Control System is starting...")
            print("✅ سیستم کنترل IoT ESP32 در حال شروع است...")
            
            # Execute the main asynchronous function
            asyncio.run(self.run_async())
            
        except Exception as e:
            print(f"❌ Critical system error: {e}")
            print(f"❌ خطای بحرانی سیستم: {e}")
            self.shutdown()
    
    def shutdown(self):
        """
        Perform graceful system shutdown and cleanup.
        
        Safely turns off all devices, stops timers, closes network
        connections, and releases system resources. Ensures the
        system can be restarted cleanly.
        
        This method handles cleanup even if some components fail,
        providing robust shutdown behavior.
        """
        try:
            print("🛑 Shutting down ESP32 IoT Control System...")
            print("🛑 خاموش کردن سیستم کنترل IoT ESP32...")
            
            # Turn off all relay-controlled devices
            if self.relay_controller:
                self.relay_controller.off_all()
                print("✅ All relays turned off - همه رله‌ها خاموش شدند")
            
            # Stop and cleanup all automatic shutdown timers
            for timer in self.auto_off_timers.values():
                timer.deinit()
            self.auto_off_timers.clear()
            
            # Stop task scheduler timer
            if hasattr(self, 'task_timer'):
                self.task_timer.deinit()
            
            # Stop web server and close connections
            if self.web_server:
                self.web_server.stop()
                print("✅ Web server stopped - وب‌سرور متوقف شد")
            
            print("✅ System shutdown complete - خاموش کردن سیستم کامل شد")
            
        except Exception as e:
            print(f"❌ Shutdown error: {e}")
            print(f"❌ خطا در خاموش کردن: {e}")


# ============================================================================
# MAIN EXECUTION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    """
    Main execution entry point for ESP32 IoT Control System.
    
    Creates and starts the ESP32Controller instance when the module
    is run directly. Initializes all system components and begins
    the main control loop.
    """
    controller = ESP32Controller()
    controller.run()
