"""
SA5X Text Controller - Text-based protocol communication
Based on the working sa5x_controller.py from the root directory
"""

import serial
import time
import logging
from typing import Dict, Any, Optional


class SA5XController:
    """Controller for SA5X Rubidium Generator using text-based protocol"""
    
    def __init__(self, port: str, baudrate: int = 57600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Connect to SA5X via serial port"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.logger.info(f"Connected to SA5X on {self.port} at {self.baudrate} baud")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to SA5X: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from SA5X"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.info("Disconnected from SA5X")
    
    def send_command(self, command: str) -> Optional[str]:
        """Send command to SA5X and receive response"""
        if not self.serial or not self.serial.is_open:
            if not self.connect():
                return None
        
        try:
            # Send command with newline
            full_command = command + "\r\n"
            self.serial.write(full_command.encode('ascii'))
            
            # Read response
            response = self.serial.readline().decode('ascii').strip()
            return response
            
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return None
    
    def get_parameter(self, param_name: str) -> Optional[str]:
        """Get parameter value from SA5X"""
        command = f"{{get,{param_name}}}"
        return self.send_command(command)
    
    def get_status(self) -> str:
        """Get SA5X status"""
        # Check if locked
        locked_resp = self.get_parameter("Locked")
        if locked_resp and locked_resp.lower() == "true":
            return "LOCKED"
        
        # Check if in holdover
        holdover_resp = self.get_parameter("Holdover")
        if holdover_resp and holdover_resp.lower() == "true":
            return "HOLDOVER"
        
        # Check disciplining status
        disc_resp = self.get_parameter("Disciplining")
        if disc_resp and disc_resp == "1":
            return "DISCIPLINING"
        
        # Check PPS detection
        pps_resp = self.get_parameter("PpsInDetected")
        if pps_resp and pps_resp.lower() == "false":
            return "NO_PPS"
        
        return "WARMING_UP"
    
    def get_frequency_error(self) -> float:
        """Get frequency error (Phase parameter)"""
        response = self.get_parameter("Phase")
        if response:
            try:
                # Phase is in nanoseconds, convert to parts per billion
                phase_ns = float(response)
                # Approximate frequency error from phase
                return phase_ns / 1e9
            except:
                pass
        return 0.0
    
    def get_temperature(self) -> float:
        """Get temperature - SA5X may not provide this directly"""
        # Try to get temperature if available
        response = self.get_parameter("Temperature")
        if response:
            try:
                return float(response)
            except:
                pass
        # Return a placeholder if not available
        return 25.0
    
    def get_voltage(self) -> float:
        """Get supply voltage"""
        response = self.get_parameter("Voltage")
        if response:
            try:
                return float(response)
            except:
                pass
        return 0.0
    
    def get_current(self) -> float:
        """Get supply current"""
        response = self.get_parameter("Current")
        if response:
            try:
                return float(response)
            except:
                pass
        return 0.0
    
    def get_lock_status(self) -> bool:
        """Get lock status"""
        response = self.get_parameter("Locked")
        return response and response.lower() == "true"
    
    def get_holdover_status(self) -> bool:
        """Get holdover status"""
        response = self.get_parameter("Holdover")
        return response and response.lower() == "true"
    
    def start_holdover(self) -> bool:
        """Start holdover mode - disable disciplining"""
        response = self.send_command("{set,Disciplining,0}")
        return response is not None
    
    def stop_holdover(self) -> bool:
        """Stop holdover mode - enable disciplining"""
        response = self.send_command("{set,Disciplining,1}")
        return response is not None
    
    def get_all_parameters(self) -> Dict[str, Any]:
        """Get all SA5X parameters"""
        params = {
            'status': self.get_status(),
            'frequency_error': self.get_frequency_error(),
            'temperature': self.get_temperature(),
            'voltage': self.get_voltage(),
            'current': self.get_current(),
            'lock_status': self.get_lock_status(),
            'holdover_status': self.get_holdover_status()
        }
        
        # Add raw parameters for debugging
        raw_params = [
            "Locked", "Phase", "Disciplining", "PpsInDetected",
            "LockProgress", "DigitalTuning", "LastCorrection"
        ]
        
        for param in raw_params:
            value = self.get_parameter(param)
            if value:
                params[f'raw_{param}'] = value
        
        return params
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()