# ESP32 IoT Control System

A comprehensive IoT control system built with ESP32 microcontroller, featuring web-based device control, task scheduling, and real-time monitoring capabilities.

## 🚀 Features

### Hardware Control
- **4-Channel Relay Control**: Independent control of pumps and DC motor
- **Servo Motor Control**: PCA9685-based servo positioning (0-180°)
- **WiFi Connectivity**: Automatic connection with NTP time synchronization
- **Real-time Monitoring**: System status and device state tracking

### Software Features
- **Asynchronous Web Server**: REST API for device control
- **Task Scheduling**: Automated device operations with timing
- **Bilingual Support**: English and Persian language support
- **Memory Management**: Automatic garbage collection and optimization
- **Error Handling**: Graceful error recovery and logging

### Web Interface
- **Streamlit Dashboard**: User-friendly control interface
- **Real-time Updates**: Live device status monitoring
- **Scheduled Operations**: Task creation and management
- **Mobile Responsive**: Works on all device sizes

## 🛠 Hardware Requirements

### ESP32 Development Board
- ESP32-WROOM-32 or compatible
- Minimum 4MB flash memory
- WiFi capability

### Additional Components
- 4-channel relay module (5V)
- PCA9685 PWM driver board
- Servo motor (SG90 or compatible)
- Jumper wires and breadboard
- 5V power supply

### Pin Configuration
```
Relay Control:
- Relay 1 (Pump 1): GPIO 13
- Relay 2 (Pump 2): GPIO 12
- Relay 3 (Pump 3): GPIO 14
- Relay 4 (DC Motor): GPIO 27

I2C (PCA9685):
- SDA: GPIO 21
- SCL: GPIO 22

Servo:
- Connected to PCA9685 Channel 0
```

## 📦 Installation

### ESP32 Setup

1. **Install MicroPython** on your ESP32:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
   esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-micropython.bin
   ```

2. **Upload Project Files**:
   ```bash
   # Upload all files in esp-board/ directory to ESP32
   ampy --port /dev/ttyUSB0 put esp-board/boot.py
   ampy --port /dev/ttyUSB0 put esp-board/config.py
   ampy --port /dev/ttyUSB0 put esp-board/main_board.py
   ampy --port /dev/ttyUSB0 mkdir lib
   ampy --port /dev/ttyUSB0 put esp-board/lib/ lib/
   ```

3. **Configure WiFi** in `config.py`:
   ```python
   WIFI_CONFIG = {
       'ssid': 'Your_WiFi_Name',
       'password': 'Your_WiFi_Password',
       'timeout': 10,
       'timezone_offset': 3.5  # Iran timezone
   }
   ```

### Computer Interface Setup

1. **Install Python Dependencies**:
   ```bash
   pip install streamlit requests pandas
   ```

2. **Run the Control Interface**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 🌐 API Documentation

### Base URL
```
http://[ESP32_IP_ADDRESS]/
```

### Endpoints

#### Relay Control
```http
GET /relay/{channel}/{action}?duration={seconds}
```
- **channel**: 0-3 (relay channel number)
- **action**: `on` or `off`
- **duration**: Optional auto-off timer (seconds)

**Example:**
```http
GET /relay/0/on?duration=30
```

#### Servo Control
```http
GET /servo/{angle}
```
- **angle**: 0-180 (degrees)

**Example:**
```http
GET /servo/90
```

#### System Status
```http
GET /status
```

**Response:**
```json
{
    "status": "success",
    "time": {
        "year": 2024,
        "month": 6,
        "day": 6,
        "hour": 14,
        "minute": 30,
        "second": 45
    },
    "relays": "operational",
    "servo": "operational"
}
```

## 📱 Web Interface Usage

### Device Control
1. Open the Streamlit dashboard
2. Enter your ESP32's IP address
3. Use the control buttons to operate devices
4. Monitor real-time status updates

### Task Scheduling
1. Navigate to "Timed Operations" page
2. Select device, date, time, and duration
3. Click "Add Task" to schedule
4. View and manage scheduled tasks

### System Monitoring
1. Check connection status indicator
2. View current system time
3. Monitor device states
4. Review operation logs

## 🔧 Configuration

### Device Settings (`config.py`)
```python
DEVICE_CONFIG = {
    'pump1': {
        'channel': 0,
        'max_duration': 300,  # 5 minutes
        'name_en': 'Water Pump 1',
        'name_fa': 'پمپ آب ۱'
    },
    # ... more devices
}
```

### System Settings
```python
SYSTEM_CONFIG = {
    'debug_mode': False,
    'memory_threshold': 50000,  # bytes
    'max_concurrent_connections': 5
}
```

## 🚨 Safety Features

- **Maximum Duration Limits**: Prevents device overrun
- **Automatic Shutdown**: Timer-based device protection
- **Memory Monitoring**: Prevents system crashes
- **Error Recovery**: Graceful handling of failures
- **WiFi Reconnection**: Automatic network recovery

## 🔍 Troubleshooting

### Common Issues

1. **ESP32 Not Connecting to WiFi**
   - Check SSID and password in config.py
   - Verify WiFi signal strength
   - Restart ESP32

2. **Devices Not Responding**
   - Check GPIO connections
   - Verify relay module power supply
   - Test individual components

3. **Web Interface Connection Failed**
   - Confirm ESP32 IP address
   - Check network connectivity
   - Verify firewall settings

### Debug Mode
Enable debug mode in `config.py`:
```python
SYSTEM_CONFIG = {
    'debug_mode': True
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Erfan Mohamadnia**
- GitHub: [@erfanmohamadnia](https://github.com/erfanmohamadnia)
- Email: erfan.mohamadnia@example.com

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📊 Project Status

- ✅ Hardware control implementation
- ✅ Web server and API
- ✅ Task scheduling system
- ✅ Streamlit dashboard
- ✅ Documentation
- 🔄 Mobile app (planned)
- 🔄 Advanced analytics (planned)

## 🙏 Acknowledgments

- MicroPython community for excellent documentation
- Streamlit team for the amazing framework
- ESP32 community for hardware support and examples

---

**Generated by Copilot** - Professional IoT Control System for ESP32
