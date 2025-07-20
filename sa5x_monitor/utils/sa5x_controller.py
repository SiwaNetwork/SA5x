"""
SA5X Controller - Communication and data acquisition
Based on Timetickler project
"""

import serial
import time
import logging
import struct
from typing import Dict, Any, Optional, Tuple


class SA5XController:
    """Controller for SA5X Rubidium Generator"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.logger = logging.getLogger(__name__)
        
        # SA5X command constants
        self.COMMANDS = {
            'GET_STATUS': b'\x01',
            'GET_FREQ_ERROR': b'\x02',
            'GET_TEMPERATURE': b'\x03',
            'GET_VOLTAGE': b'\x04',
            'GET_CURRENT': b'\x05',
            'GET_LOCK_STATUS': b'\x06',
            'GET_HOLDOVER_STATUS': b'\x07',
            'START_HOLDOVER': b'\x08',
            'STOP_HOLDOVER': b'\x09',
            'GET_CONFIG': b'\x0A',
            'SET_CONFIG': b'\x0B'
        }
        
        # Status codes
        self.STATUS_CODES = {
            0x00: 'OK',
            0x01: 'LOCKED',
            0x02: 'HOLDOVER',
            0x03: 'WARMING_UP',
            0x04: 'ERROR',
            0x05: 'NOT_LOCKED'
        }
        
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
            self.logger.info(f"Connected to SA5X on {self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to SA5X: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from SA5X"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.info("Disconnected from SA5X")
    
    def send_command(self, command: bytes, data: bytes = b'') -> Optional[bytes]:
        """Send command to SA5X and receive response"""
        if not self.serial or not self.serial.is_open:
            if not self.connect():
                return None
        
        try:
            # Format: [START][LENGTH][COMMAND][DATA][CHECKSUM]
            start_byte = b'\xAA'
            length = len(data) + 1  # +1 for command byte
            packet = start_byte + bytes([length]) + command + data
            
            # Calculate checksum (simple XOR)
            checksum = 0
            for byte in packet[1:]:
                checksum ^= byte
            packet += bytes([checksum])
            
            self.serial.write(packet)
            self.serial.flush()
            
            # Read response
            response = self._read_response()
            return response
            
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return None
    
    def _read_response(self) -> Optional[bytes]:
        """Read response from SA5X"""
        try:
            # Wait for start byte
            start_byte = self.serial.read(1)
            if not start_byte or start_byte[0] != 0xAA:
                return None
            
            # Read length
            length_byte = self.serial.read(1)
            if not length_byte:
                return None
            length = length_byte[0]
            
            # Read data
            data = self.serial.read(length)
            if len(data) != length:
                return None
            
            # Read checksum
            checksum_byte = self.serial.read(1)
            if not checksum_byte:
                return None
            
            # Verify checksum
            calculated_checksum = 0
            for byte in data:
                calculated_checksum ^= byte
            calculated_checksum ^= length
            
            if calculated_checksum != checksum_byte[0]:
                self.logger.warning("Checksum verification failed")
                return None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to read response: {e}")
            return None
    
    def get_status(self) -> str:
        """Get SA5X status"""
        response = self.send_command(self.COMMANDS['GET_STATUS'])
        if response and len(response) >= 1:
            status_code = response[0]
            return self.STATUS_CODES.get(status_code, 'UNKNOWN')
        return 'ERROR'
    
    def get_frequency_error(self) -> float:
        """Get frequency error in parts per million"""
        response = self.send_command(self.COMMANDS['GET_FREQ_ERROR'])
        if response and len(response) >= 4:
            # Frequency error is stored as 32-bit float
            freq_error = struct.unpack('f', response[:4])[0]
            return freq_error
        return 0.0
    
    def get_temperature(self) -> float:
        """Get temperature in Celsius"""
        response = self.send_command(self.COMMANDS['GET_TEMPERATURE'])
        if response and len(response) >= 4:
            # Temperature is stored as 32-bit float
            temperature = struct.unpack('f', response[:4])[0]
            return temperature
        return 0.0
    
    def get_voltage(self) -> float:
        """Get supply voltage in volts"""
        response = self.send_command(self.COMMANDS['GET_VOLTAGE'])
        if response and len(response) >= 4:
            voltage = struct.unpack('f', response[:4])[0]
            return voltage
        return 0.0
    
    def get_current(self) -> float:
        """Get supply current in amperes"""
        response = self.send_command(self.COMMANDS['GET_CURRENT'])
        if response and len(response) >= 4:
            current = struct.unpack('f', response[:4])[0]
            return current
        return 0.0
    
    def get_lock_status(self) -> bool:
        """Get lock status"""
        response = self.send_command(self.COMMANDS['GET_LOCK_STATUS'])
        if response and len(response) >= 1:
            return response[0] == 0x01
        return False
    
    def get_holdover_status(self) -> bool:
        """Get holdover status"""
        response = self.send_command(self.COMMANDS['GET_HOLDOVER_STATUS'])
        if response and len(response) >= 1:
            return response[0] == 0x01
        return False
    
    def start_holdover(self) -> bool:
        """Start holdover mode"""
        response = self.send_command(self.COMMANDS['START_HOLDOVER'])
        return response is not None and len(response) >= 1 and response[0] == 0x00
    
    def stop_holdover(self) -> bool:
        """Stop holdover mode"""
        response = self.send_command(self.COMMANDS['STOP_HOLDOVER'])
        return response is not None and len(response) >= 1 and response[0] == 0x00
    
    def get_all_parameters(self) -> Dict[str, Any]:
        """Get all SA5X parameters"""
        return {
            'status': self.get_status(),
            'frequency_error': self.get_frequency_error(),
            'temperature': self.get_temperature(),
            'voltage': self.get_voltage(),
            'current': self.get_current(),
            'lock_status': self.get_lock_status(),
            'holdover_status': self.get_holdover_status()
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()