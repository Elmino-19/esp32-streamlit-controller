import requests
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import urljoin

@dataclass
class CommandResponse:
    """Represents the response from ESP32 after sending a command."""
    success: bool
    message: str
    response_data: Optional[str] = None
    error_code: Optional[int] = None
    status_code: Optional[int] = None

class ESP32Client:
    """
    HTTP-based ESP32 client for relay control.
    Communicates with ESP32 web server using HTTP requests.
    """
    
    def __init__(self, host: str = "192.168.1.100", port: int = 80, timeout: int = 5):
        """
        Initialize ESP32 client with connection parameters.
        
        :param host: ESP32 IP address
        :param port: ESP32 web server port (usually 80)
        :param timeout: HTTP request timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}"
        self.is_connected = False
        self.logger = logging.getLogger(__name__)
        
        # Create persistent session for better performance
        self.session = requests.Session()
        self.session.timeout = timeout
        
    def connect(self) -> bool:
        """
        Test connection to ESP32 web server.
        
        :return: True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Testing connection to ESP32 at {self.base_url}")
            
            # Try to connect to root endpoint or status endpoint
            test_endpoints = ["/", "/status", "/ping"]
            
            for endpoint in test_endpoints:
                try:
                    response = self.session.get(
                        urljoin(self.base_url, endpoint),
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        self.is_connected = True
                        self.logger.info(f"Successfully connected to ESP32 via {endpoint}")
                        return True
                        
                except requests.exceptions.RequestException:
                    continue
            
            # If no endpoint worked, try a simple connection test
            response = self.session.get(self.base_url, timeout=self.timeout)
            if response.status_code in [200, 404]:  # 404 is also acceptable
                self.is_connected = True
                self.logger.info("Successfully connected to ESP32")
                return True
            else:
                self.logger.error(f"Unexpected status code: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectTimeout:
            self.logger.error(f"Connection timeout to {self.base_url}")
            return False
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error to {self.base_url}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close session and mark as disconnected."""
        self.logger.info("Disconnecting from ESP32")
        self.is_connected = False
        self.session.close()
    
    def send_device_command(self, device_id: int, action: str, duration: int = 0) -> CommandResponse:
        """
        Send device control command to ESP32 via HTTP.
        
        :param device_id: Device/relay ID (1-8 typically)
        :param action: "ON" or "OFF"
        :param duration: Duration in seconds for timed operations
        :return: CommandResponse with operation result
        """
        if not self.is_connected:
            return CommandResponse(False, "Not connected to ESP32")
        
        # Try different common ESP32 URL patterns
        url_patterns = [
            f"/relay/{device_id}/{action.lower()}",  # /relay/1/on
            f"/relay{device_id}/{action.lower()}",   # /relay1/on
            f"/gpio/{device_id}/{action.lower()}",   # /gpio/1/on
            f"/control?relay={device_id}&action={action.lower()}",  # Query parameters
            f"/{action.lower()}{device_id}",         # /on1
        ]
        
        # Add duration parameter if specified
        if duration > 0:
            url_patterns = [
                f"/relay/{device_id}/{action.lower()}?duration={duration}",
                f"/relay{device_id}/{action.lower()}?duration={duration}",
                f"/control?relay={device_id}&action={action.lower()}&duration={duration}",
            ]
        
        self.logger.info(f"Sending command: Device {device_id} -> {action}" + 
                        (f" for {duration}s" if duration > 0 else ""))
        
        # Try each URL pattern until one works
        for url_pattern in url_patterns:
            full_url = urljoin(self.base_url, url_pattern)
            response = self._send_http_request(full_url, "GET")
            
            if response.success:
                self.logger.info(f"Command successful using URL: {url_pattern}")
                return response
            else:
                self.logger.debug(f"Failed with URL pattern: {url_pattern}")
        
        # If GET requests don't work, try POST
        for url_pattern in ["/relay", "/control", "/command"]:
            full_url = urljoin(self.base_url, url_pattern)
            data = {
                "relay": device_id,
                "action": action.lower(),
            }
            if duration > 0:
                data["duration"] = duration
                
            response = self._send_http_request(full_url, "POST", data=data)
            if response.success:
                self.logger.info(f"Command successful using POST to: {url_pattern}")
                return response
        
        return CommandResponse(False, "All URL patterns failed")
    
    def _send_http_request(self, url: str, method: str = "GET", data: Optional[Dict] = None) -> CommandResponse:
        """
        Send HTTP request to ESP32.
        
        :param url: Full URL to request
        :param method: HTTP method (GET or POST)
        :param data: POST data if applicable
        :return: CommandResponse with result
        """
        try:
            self.logger.debug(f"Sending {method} request to: {url}")
            
            if method.upper() == "POST":
                response = self.session.post(url, data=data, timeout=self.timeout)
            else:
                response = self.session.get(url, timeout=self.timeout)
            
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Response content: {response.text[:200]}")  # First 200 chars
            
            # Consider various success conditions
            if response.status_code == 200:
                # Check response content for success indicators
                content = response.text.lower()
                if any(keyword in content for keyword in ["ok", "success", "done", "relay"]):
                    return CommandResponse(
                        True, 
                        "Command executed successfully", 
                        response.text,
                        status_code=response.status_code
                    )
                else:
                    return CommandResponse(
                        True,  # Still consider it success if status is 200
                        "Command sent (no explicit confirmation)",
                        response.text,
                        status_code=response.status_code
                    )
            elif response.status_code == 404:
                return CommandResponse(
                    False, 
                    f"Endpoint not found: {url}",
                    response.text,
                    status_code=response.status_code
                )
            else:
                return CommandResponse(
                    False,
                    f"HTTP error {response.status_code}",
                    response.text,
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout for URL: {url}")
            return CommandResponse(False, "Request timeout")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error for URL {url}: {e}")
            self.is_connected = False  # Mark as disconnected
            return CommandResponse(False, f"Connection error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error for URL {url}: {e}")
            return CommandResponse(False, f"Unexpected error: {e}")
    
    def get_device_status(self, device_id: int) -> CommandResponse:
        """
        Get current status of a specific device.
        
        :param device_id: Device/relay ID
        :return: CommandResponse with device status
        """
        command = f"STATUS_{device_id}"
        return self._send_raw_command(command)
    
    def get_all_status(self) -> CommandResponse:
        """
        Get status of all devices.
        
        :return: CommandResponse with all device statuses
        """
        return self._send_raw_command("STATUS_ALL")
    
    def test_connection(self) -> bool:
        """
        Test if connection is still alive.
        
        :return: True if connection is working
        """
        if not self.is_connected:
            return False
        
        response = self._send_raw_command("PING")
        if not response.success:
            self.logger.warning("Connection test failed, marking as disconnected")
            self.is_connected = False
        
        return response.success
