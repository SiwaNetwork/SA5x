#!/usr/bin/env python3
"""Quick test to identify SA5X protocol"""

import serial
import time

# Test text protocol at 57600 baud
print("Testing text protocol at 57600 baud...")
try:
    ser = serial.Serial('/dev/ttyS6', 57600, timeout=1)
    ser.write(b"{get,Locked}\r\n")
    time.sleep(0.1)
    response = ser.readline()
    if response:
        print(f"✓ Got response at 57600: {response.decode('ascii', errors='ignore').strip()}")
        print("Your SA5X uses TEXT protocol at 57600 baud")
        
        # Test a few more commands
        for cmd in ["{get,Phase}", "{get,PpsInDetected}", "{get,Disciplining}"]:
            ser.write((cmd + "\r\n").encode())
            time.sleep(0.1)
            resp = ser.readline().decode('ascii', errors='ignore').strip()
            print(f"{cmd} -> {resp}")
    else:
        print("No response at 57600 baud")
    ser.close()
except Exception as e:
    print(f"Error at 57600: {e}")

print("\nTesting text protocol at 115200 baud...")
try:
    ser = serial.Serial('/dev/ttyS6', 115200, timeout=1)
    ser.write(b"{get,Locked}\r\n")
    time.sleep(0.1)
    response = ser.readline()
    if response:
        print(f"✓ Got response at 115200: {response.decode('ascii', errors='ignore').strip()}")
        print("Your SA5X uses TEXT protocol at 115200 baud")
    else:
        print("No response at 115200 baud")
    ser.close()
except Exception as e:
    print(f"Error at 115200: {e}")