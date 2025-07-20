#!/usr/bin/env python3
"""
SA5X Atomic Clock Controller
Communicates with Microchip SA5X atomic clock module via serial interface.
Default baudrate: 57600
"""

import serial
import time
import sys
from typing import Optional, Dict, Any


class SA5XController:
    """Controller class for SA5X atomic clock module"""
    
    def __init__(self, port: str = "/dev/ttyS6", baudrate: int = 57600, timeout: float = 1.0):
        """
        Initialize SA5X controller
        
        Args:
            port: Serial port (default: /dev/ttyUSB0)
            baudrate: Baud rate (default: 57600)
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        
    def connect(self) -> bool:
        """Establish serial connection to SA5X module"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            print(f"Connected to SA5X on {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Disconnected from SA5X")
    
    def send_command(self, command: str) -> Optional[str]:
        """
        Send command to SA5X module and return response
        
        Args:
            command: Command string to send
            
        Returns:
            Response string or None if failed
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("Not connected to SA5X")
            return None
        
        try:
            # Send command with newline
            full_command = command + "\r\n"
            self.serial_conn.write(full_command.encode('ascii'))
            
            # Read response
            response = self.serial_conn.readline().decode('ascii').strip()
            return response
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            return None
    
    def get_parameter(self, param_name: str) -> Optional[str]:
        """
        Get parameter value from SA5X
        
        Args:
            param_name: Parameter name
            
        Returns:
            Parameter value or None if failed
        """
        command = f"{{get,{param_name}}}"
        return self.send_command(command)
    
    def set_parameter(self, param_name: str, value: Any) -> Optional[str]:
        """
        Set parameter value on SA5X
        
        Args:
            param_name: Parameter name
            value: Parameter value
            
        Returns:
            Response string or None if failed
        """
        command = f"{{set,{param_name},{value}}}"
        return self.send_command(command)
    
    def store_configuration(self) -> Optional[str]:
        """Store current configuration to flash memory"""
        return self.send_command("{store}")
    
    # Convenience methods for common operations
    def enable_disciplining(self) -> Optional[str]:
        """Enable disciplining mode"""
        return self.set_parameter("Disciplining", 1)
    
    def disable_disciplining(self) -> Optional[str]:
        """Disable disciplining mode"""
        return self.set_parameter("Disciplining", 0)
    
    def set_pps_width(self, width: int) -> Optional[str]:
        """Set PPS pulse width in nanoseconds"""
        return self.set_parameter("PpsWidth", width)
    
    def set_pps_offset(self, offset: int) -> Optional[str]:
        """Set PPS offset in nanoseconds"""
        return self.set_parameter("PpsOffset", offset)
    
    def set_tau_pps0(self, tau: int) -> Optional[str]:
        """Set Tau for PPS0 in milliseconds"""
        return self.set_parameter("TauPps0", tau)
    
    def set_discipline_threshold_pps0(self, threshold: int) -> Optional[str]:
        """Set discipline threshold for PPS0"""
        return self.set_parameter("DisciplineThresholdPps0", threshold)
    
    def set_phase_limit(self, limit: int) -> Optional[str]:
        """Set phase limit in nanoseconds"""
        return self.set_parameter("PhaseLimit", limit)
    
    def get_status(self) -> Dict[str, str]:
        """Get comprehensive status of SA5X module"""
        status_params = [
            "Disciplining", "PpsOffset", "DisciplineLocked", "Locked",
            "Phase", "DigitalTuning", "JamSyncing", "PhaseLimit",
            "DisciplineThresholdPps0", "PpsInDetected", "LockProgress",
            "PpsSource", "LastCorrection", "TauPps0"
        ]
        
        status = {}
        for param in status_params:
            value = self.get_parameter(param)
            if value:
                status[param] = value
        
        return status
    
    def apply_minimum_configuration(self) -> bool:
        """
        Apply minimum necessary configuration as specified in user requirements
        """
        print("Applying minimum necessary configuration...")
        
        config_commands = [
            ("Disciplining", 1),
            ("PpsWidth", 80000000),
            ("TauPps0", 10000),
            ("PpsOffset", -30),
            ("DisciplineThresholdPps0", 20)
        ]
        
        success = True
        for param, value in config_commands:
            print(f"Setting {param} = {value}")
            response = self.set_parameter(param, value)
            if response:
                print(f"  Response: {response}")
            else:
                print(f"  Failed to set {param}")
                success = False
        
        if success:
            print("Storing configuration...")
            store_response = self.store_configuration()
            if store_response:
                print(f"Store response: {store_response}")
            else:
                print("Failed to store configuration")
                success = False
        
        return success


def main():
    """Main function demonstrating SA5X controller usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SA5X Atomic Clock Controller")
    parser.add_argument("--port", default="/dev/ttyS6", help="Serial port")
    parser.add_argument("--baudrate", type=int, default=57600, help="Baud rate")
    parser.add_argument("--command", help="Single command to execute")
    parser.add_argument("--get", help="Get parameter value")
    parser.add_argument("--set", nargs=2, metavar=("PARAM", "VALUE"), help="Set parameter value")
    parser.add_argument("--status", action="store_true", help="Get full status")
    parser.add_argument("--min-config", action="store_true", help="Apply minimum configuration")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    # Create controller
    controller = SA5XController(port=args.port, baudrate=args.baudrate)
    
    if not controller.connect():
        sys.exit(1)
    
    try:
        if args.command:
            # Execute single command
            response = controller.send_command(args.command)
            print(f"Command: {args.command}")
            print(f"Response: {response}")
            
        elif args.get:
            # Get parameter
            response = controller.get_parameter(args.get)
            print(f"{args.get}: {response}")
            
        elif args.set:
            # Set parameter
            param, value = args.set
            response = controller.set_parameter(param, value)
            print(f"Set {param} = {value}")
            print(f"Response: {response}")
            
        elif args.status:
            # Get full status
            status = controller.get_status()
            print("SA5X Status:")
            for param, value in status.items():
                print(f"  {param}: {value}")
                
        elif args.min_config:
            # Apply minimum configuration
            success = controller.apply_minimum_configuration()
            if success:
                print("Minimum configuration applied successfully")
            else:
                print("Failed to apply minimum configuration")
                
        elif args.interactive:
            # Interactive mode
            print("SA5X Interactive Mode")
            print("Type 'help' for available commands, 'quit' to exit")
            
            while True:
                try:
                    command = input("SA5X> ").strip()
                    
                    if command.lower() in ['quit', 'exit', 'q']:
                        break
                    elif command.lower() == 'help':
                        print("Available commands:")
                        print("  {get,PARAM} - Get parameter value")
                        print("  {set,PARAM,VALUE} - Set parameter value")
                        print("  {store} - Store configuration")
                        print("  status - Get full status")
                        print("  quit - Exit")
                    elif command.lower() == 'status':
                        status = controller.get_status()
                        for param, value in status.items():
                            print(f"  {param}: {value}")
                    else:
                        response = controller.send_command(command)
                        print(f"Response: {response}")
                        
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
                except EOFError:
                    break
        else:
            # Default: show help
            parser.print_help()
            
    finally:
        controller.disconnect()


if __name__ == "__main__":
    main()