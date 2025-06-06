"""
ESP32 IoT Control System - Configuration Module
==============================================

Central configuration file for the ESP32 IoT Control System containing all
hardware settings, network parameters, device configurations, and system constants.
This module provides a single source of truth for all system configurations.

Author: Erfan Mohamadnia
License: MIT
Version: 1.0.0

Configuration Categories:
- WiFi network settings and connection parameters
- Hardware pin assignments and I2C configurations  
- Device-specific settings for pumps, motors, and servos
- Web server and API endpoint definitions
- Task management and scheduling parameters
- System behavior and error handling settings
- Multilingual message templates (English/Persian)

Usage:
    import config
    wifi_ssid = config.WIFI_CONFIG['ssid']
    relay_pins = config.HARDWARE_CONFIG['relay_pins']
"""

# ============================================================================
# Network Configuration
# ============================================================================
WIFI_CONFIG = {
    'ssid': 'DangerZone',            # WiFi network name
    'password': 'Fs@2082099',        # WiFi network password
    'timeout': 30,                   # Connection timeout in seconds
    'timezone_offset': 3.5           # Tehran timezone offset (UTC+3:30)
}

# ============================================================================
# Hardware Configuration
# ============================================================================
HARDWARE_CONFIG = {
    # GPIO pins for relay control: [pump1, pump2, pump3, dcmotor]
    'relay_pins': [14, 25, 26, 27],
    
    # I2C bus configuration for PCA9685 servo driver
    'i2c_config': {
        'scl_pin': 22,                  # I2C clock line (SCL)
        'sda_pin': 21,                  # I2C data line (SDA)
        'pca9685_address': 0x40         # PCA9685 I2C slave address
    },
    
    # Servo motor PWM configuration
    'servo_config': {
        'channel': 0,                   # PCA9685 channel for servo
        'min_pulse_us': 500,            # Minimum pulse width (microseconds)
        'max_pulse_us': 2500,           # Maximum pulse width (microseconds)
        'frequency': 50                 # PWM frequency in Hz (standard for servos)
    }
}

# ============================================================================
# Web Server Configuration
# ============================================================================
WEB_SERVER_CONFIG = {
    'port': 80,                         # HTTP server port
    'bind_ip': '0.0.0.0',              # Bind to all network interfaces
    'max_connections': 10               # Maximum concurrent connections
}

# ============================================================================
# Task Management Configuration
# ============================================================================

TASK_CONFIG = {
    'filename': 'tasks.json',           # Task storage file
    'max_tasks': 50,                    # Maximum number of scheduled tasks
    'check_interval': 60                # Task check interval in seconds
}

# ============================================================================
# Device Configuration and Limits
# ============================================================================
DEVICE_CONFIG = {
    'pump1': {
        'name': 'Water Pump 1',         # English device name
        'name_fa': 'پمپ آب 1',          # Persian device name
        'channel': 0,                   # Relay channel assignment
        'max_duration': 3600            # Maximum runtime in seconds (1 hour)
    },
    'pump2': {
        'name': 'Water Pump 2', 
        'name_fa': 'پمپ آب 2',
        'channel': 1,
        'max_duration': 3600
    },
    'pump3': {
        'name': 'Water Pump 3',
        'name_fa': 'پمپ آب 3', 
        'channel': 2,
        'max_duration': 3600
    },
    'dcmotor': {
        'name': 'DC Motor',
        'name_fa': 'موتور DC',
        'channel': 3,
        'max_duration': 7200            # 2 hours maximum runtime
    },
    'servo': {
        'name': 'Servo Motor',
        'name_fa': 'موتور سروو',
        'min_angle': 0,                 # Minimum servo angle (degrees)
        'max_angle': 180                # Maximum servo angle (degrees)
    }
}

# ============================================================================
# System Configuration
# ============================================================================
SYSTEM_CONFIG = {
    'debug_mode': False,                # Enable verbose debug output
    'auto_gc_interval': 30,             # Automatic garbage collection interval (seconds)
    'status_update_interval': 10,       # Status update interval for web interface (seconds)
    'memory_threshold': 10000,          # Minimum free memory threshold (bytes)
    'restart_on_error': True,           # Auto-restart system on critical errors
}

# ============================================================================
# API Routes and Endpoints
# ============================================================================
API_ROUTES = {
    # Primary ESP32 web server endpoints (active routes)
    'relay_control': '/relay/<channel>/<action>',     # Control relay: /relay/0/on, /relay/1/off
    'servo_control': '/servo/<angle>',                # Control servo: /servo/90
    'status': '/status',                              # System status and diagnostics
    
    # Legacy API endpoints (maintained for backward compatibility)
    'pump_control': '/api/pump/<id>/<action>',        # Legacy pump control
    'pump_timed': '/api/pump/<id>/on/<duration>',     # Legacy timed pump operation
    'dcmotor_control': '/api/dcmotor/<action>',       # Legacy DC motor control
    'dcmotor_timed': '/api/dcmotor/on/<duration>',    # Legacy timed DC motor operation
    'time': '/api/time',                              # Current system time
    'tasks': '/api/tasks',                            # Task management
    'task_add': '/api/task/add',                      # Add new scheduled task
    'task_delete': '/api/task/<id>/delete'            # Delete scheduled task
}

# ============================================================================
# Default Values and Constants
# ============================================================================
DEFAULTS = {
    'pump_duration': 30,                # Default pump runtime (seconds)
    'dcmotor_duration': 60,             # Default DC motor runtime (seconds)
    'servo_angle': 90,                  # Default servo position (degrees)
    'task_check_tolerance': 2           # Time tolerance for task execution (seconds)
}

# ============================================================================
# Multilingual Message Templates
# ============================================================================
# Error message templates for system failures and validation errors
ERROR_MESSAGES = {
    'wifi_connection_failed': {
        'en': 'Failed to connect to WiFi network',
        'fa': 'اتصال به شبکه WiFi ناموفق بود'
    },
    'hardware_init_failed': {
        'en': 'Hardware initialization failed',
        'fa': 'مقداردهی سخت‌افزار ناموفق بود'
    },
    'invalid_device': {
        'en': 'Invalid device specified',
        'fa': 'دستگاه نامعتبر مشخص شده'
    },
    'task_limit_reached': {
        'en': 'Maximum number of tasks reached',
        'fa': 'حداکثر تعداد تسک‌ها به پایان رسید'
    },
    'duration_too_long': {
        'en': 'Duration exceeds maximum allowed time',
        'fa': 'مدت زمان از حداکثر مجاز بیشتر است'
    }
}

# Success message templates for completed operations
SUCCESS_MESSAGES = {
    'device_on': {
        'en': '{device} turned ON',
        'fa': '{device} روشن شد'
    },
    'device_off': {
        'en': '{device} turned OFF', 
        'fa': '{device} خاموش شد'
    },
    'device_timed': {
        'en': '{device} turned ON for {duration} seconds',
        'fa': '{device} برای {duration} ثانیه روشن شد'
    },
    'servo_moved': {
        'en': 'Servo moved to {angle} degrees',
        'fa': 'سروو به {angle} درجه حرکت کرد'
    },
    'task_scheduled': {
        'en': 'Task scheduled successfully',
        'fa': 'تسک با موفقیت برنامه‌ریزی شد'
    },
    'task_deleted': {
        'en': 'Task deleted successfully',
        'fa': 'تسک با موفقیت حذف شد'
    }
}

# ============================================================================
# Web Interface Configuration
# ============================================================================
WEB_INTERFACE = {
    'title': 'ESP32 IoT Control System',        # Application title
    'title_fa': 'سیستم کنترل IoT ESP32',       # Persian application title
    'theme_color': '#2196F3',                   # Primary theme color (Material Blue)
    'auto_refresh': True,                       # Enable automatic page refresh
    'refresh_interval': 10000,                  # Auto-refresh interval (milliseconds)
    'show_persian': True,                       # Display Persian text alongside English
    'default_language': 'en'                    # Default interface language (en/fa)
}
