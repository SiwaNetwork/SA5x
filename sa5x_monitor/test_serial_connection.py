#!/usr/bin/env python3
"""
Test serial port connection
"""

import os
import sys
import serial
import glob

def list_serial_ports():
    """List all available serial ports"""
    print("Searching for serial ports...")
    
    # Common serial port patterns
    patterns = ['/dev/ttyS*', '/dev/ttyUSB*', '/dev/ttyACM*', '/dev/tty.*']
    
    ports = []
    for pattern in patterns:
        ports.extend(glob.glob(pattern))
    
    if ports:
        print(f"\nFound {len(ports)} serial ports:")
        for port in sorted(ports):
            try:
                # Check if we can access the port
                if os.path.exists(port):
                    readable = os.access(port, os.R_OK)
                    writable = os.access(port, os.W_OK)
                    print(f"  {port} - Readable: {readable}, Writable: {writable}")
            except Exception as e:
                print(f"  {port} - Error checking: {e}")
    else:
        print("No serial ports found!")
    
    return ports

def test_port(port, baudrate=115200):
    """Test connection to a specific port"""
    print(f"\nTesting connection to {port} at {baudrate} baud...")
    
    # Check if port exists
    if not os.path.exists(port):
        print(f"ERROR: Port {port} does not exist!")
        return False
    
    # Check permissions
    if not os.access(port, os.R_OK):
        print(f"ERROR: No read permission for {port}")
        print("Try: sudo chmod 666 {} or add user to dialout group".format(port))
        return False
    
    if not os.access(port, os.W_OK):
        print(f"ERROR: No write permission for {port}")
        print("Try: sudo chmod 666 {} or add user to dialout group".format(port))
        return False
    
    # Try to open the port
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        
        if ser.is_open:
            print(f"SUCCESS: Connected to {port}")
            print(f"  Port settings: {ser.baudrate} baud, {ser.bytesize} bits, {ser.parity} parity, {ser.stopbits} stop bits")
            
            # Try to send a test command
            print("  Sending test data...")
            test_data = b'\xAA\x01\x01\x00'  # Simple test packet
            ser.write(test_data)
            ser.flush()
            
            # Try to read response
            print("  Waiting for response (1 second)...")
            response = ser.read(10)  # Read up to 10 bytes
            if response:
                print(f"  Received: {response.hex()}")
            else:
                print("  No response received (device may not be connected)")
            
            ser.close()
            return True
        else:
            print(f"ERROR: Port opened but is not active")
            return False
            
    except serial.SerialException as e:
        print(f"SERIAL ERROR: {e}")
        return False
    except PermissionError as e:
        print(f"PERMISSION ERROR: {e}")
        print("Try running with sudo or add user to dialout group:")
        print("  sudo usermod -a -G dialout $USER")
        print("  Then logout and login again")
        return False
    except OSError as e:
        print(f"OS ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {type(e).__name__}: {e}")
        return False

def main():
    print("SA5X Serial Port Connection Test")
    print("=" * 40)
    
    # List all available ports
    ports = list_serial_ports()
    
    # Test specific port
    test_port_name = "/dev/ttyS6"
    if len(sys.argv) > 1:
        test_port_name = sys.argv[1]
    
    print(f"\nTesting specific port: {test_port_name}")
    test_port(test_port_name)
    
    # Check user groups
    print("\nChecking user groups...")
    import subprocess
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        print(f"Current user groups: {result.stdout.strip()}")
        if 'dialout' not in result.stdout:
            print("WARNING: User is not in 'dialout' group!")
            print("To fix: sudo usermod -a -G dialout $USER")
    except:
        pass

if __name__ == "__main__":
    main()