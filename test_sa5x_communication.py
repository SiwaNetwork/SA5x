#!/usr/bin/env python3
"""
SA5X Communication Test Script
Tests both text-based and binary protocols
"""

import serial
import time
import sys

def test_text_protocol(port="/dev/ttyS6", baudrate=57600):
    """Test text-based protocol (like {get,param})"""
    print(f"\n=== Testing Text-Based Protocol ===")
    print(f"Port: {port}, Baudrate: {baudrate}")
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        print("Serial port opened successfully")
        
        # Test commands
        test_commands = [
            "{get,Locked}",
            "{get,Phase}",
            "{get,PpsInDetected}",
            "{get,LockProgress}",
            "{get,Disciplining}"
        ]
        
        for cmd in test_commands:
            print(f"\nSending: {cmd}")
            ser.write((cmd + "\r\n").encode('ascii'))
            time.sleep(0.1)
            
            response = ser.readline().decode('ascii', errors='ignore').strip()
            print(f"Response: {response}")
            
            # Also check if there's more data
            if ser.in_waiting > 0:
                extra = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
                print(f"Extra data: {extra}")
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_binary_protocol(port="/dev/ttyS6", baudrate=115200):
    """Test binary protocol with checksums"""
    print(f"\n=== Testing Binary Protocol ===")
    print(f"Port: {port}, Baudrate: {baudrate}")
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        print("Serial port opened successfully")
        
        # Send a simple status command
        # Format: [START=0xAA][LENGTH][COMMAND][CHECKSUM]
        start_byte = 0xAA
        command = 0x01  # GET_STATUS
        length = 1  # Just the command byte
        
        packet = bytes([start_byte, length, command])
        checksum = length ^ command
        packet += bytes([checksum])
        
        print(f"Sending binary packet: {packet.hex()}")
        ser.write(packet)
        time.sleep(0.1)
        
        # Read any response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"Response: {response.hex()}")
            print(f"Response (ASCII): {response.decode('ascii', errors='ignore')}")
        else:
            print("No response received")
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_raw_communication(port="/dev/ttyS6", baudrates=[57600, 115200, 9600, 19200, 38400]):
    """Test raw communication at different baudrates"""
    print(f"\n=== Testing Raw Communication ===")
    
    for baudrate in baudrates:
        print(f"\n--- Testing baudrate: {baudrate} ---")
        try:
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.5,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Send a simple newline to see if we get any response
            ser.write(b"\r\n")
            time.sleep(0.1)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"Got response: {response}")
                print(f"ASCII: {response.decode('ascii', errors='ignore')}")
                
                # Try a text command
                ser.write(b"{get,Locked}\r\n")
                time.sleep(0.1)
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting)
                    print(f"Command response: {response.decode('ascii', errors='ignore').strip()}")
                    print(f"✓ Baudrate {baudrate} seems to work!")
            else:
                print("No response")
            
            ser.close()
            
        except Exception as e:
            print(f"Error at {baudrate}: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test SA5X communication protocols")
    parser.add_argument("--port", default="/dev/ttyS6", help="Serial port")
    parser.add_argument("--protocol", choices=["text", "binary", "raw", "all"], 
                       default="all", help="Protocol to test")
    
    args = parser.parse_args()
    
    if args.protocol in ["text", "all"]:
        test_text_protocol(args.port)
    
    if args.protocol in ["binary", "all"]:
        test_binary_protocol(args.port)
    
    if args.protocol in ["raw", "all"]:
        test_raw_communication(args.port)

if __name__ == "__main__":
    main()