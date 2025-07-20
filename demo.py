#!/usr/bin/env python3
"""
SA5X Controller Demo
Demonstrates how to use the SA5X atomic clock controller.
"""

from sa5x_controller import SA5XController
import sys


def demo_basic_usage():
    """Demonstrate basic usage of the SA5X controller"""
    print("=== SA5X Controller Demo ===\n")
    
    # Create controller instance
    controller = SA5XController(port="/dev/ttyS6", baudrate=57600)
    
    print("1. Creating SA5X controller instance")
    print(f"   Port: {controller.port}")
    print(f"   Baudrate: {controller.baudrate}")
    print()
    
    # Note: In a real scenario, you would connect here
    print("2. Connection (simulated)")
    print("   In real usage, controller.connect() would establish serial connection")
    print("   Example: controller.connect()")
    print()
    
    print("3. Available methods:")
    print("   - controller.get_parameter('PpsOffset')")
    print("   - controller.set_parameter('PpsOffset', -30)")
    print("   - controller.store_configuration()")
    print("   - controller.apply_minimum_configuration()")
    print("   - controller.get_status()")
    print()
    
    print("4. Command line usage:")
    print("   python sa5x_controller.py --get PpsOffset")
    print("   python sa5x_controller.py --set PpsOffset -30")
    print("   python sa5x_controller.py --status")
    print("   python sa5x_controller.py --min-config")
    print("   python sa5x_controller.py --interactive")
    print()


def demo_commands():
    """Show all the commands supported by the program"""
    print("=== Supported Commands ===\n")
    
    print("Minimum Configuration Commands:")
    print("  {set,Disciplining,1}")
    print("  {set,PpsWidth,80000000}")
    print("  {set,TauPps0,10000}")
    print("  {set,PpsOffset,-30}")
    print("  {set,DisciplineThresholdPps0,20}")
    print("  {store}")
    print()
    
    print("Get Commands:")
    get_commands = [
        "PpsOffset", "DisciplineLocked", "Locked", "Disciplining",
        "Phase", "TauPps0", "DigitalTuning", "JamSyncing",
        "PhaseLimit", "DisciplineThresholdPps0", "PpsInDetected",
        "LockProgress", "PpsSource", "LastCorrection"
    ]
    
    for cmd in get_commands:
        print(f"  {{get,{cmd}}}")
    print()
    
    print("Set Commands:")
    set_commands = [
        ("PpsOffset", "value"),
        ("PpsWidth", "value"),
        ("Disciplining", "value"),
        ("TauPps0", "value"),
        ("PhaseLimit", "value"),
        ("DisciplineThresholdPps0", "value")
    ]
    
    for param, value in set_commands:
        print(f"  {{set,{param},{value}}}")
    print()
    
    print("Store Command:")
    print("  {store}")
    print()


def demo_python_usage():
    """Show Python code examples"""
    print("=== Python Usage Examples ===\n")
    
    print("Basic usage:")
    print("""
from sa5x_controller import SA5XController

# Create controller
controller = SA5XController(port="/dev/ttyS6", baudrate=57600)

# Connect to device
if controller.connect():
    # Get parameter
    offset = controller.get_parameter("PpsOffset")
    print(f"PPS Offset: {offset}")
    
    # Set parameter
    controller.set_parameter("PpsOffset", -30)
    
    # Store configuration
    controller.store_configuration()
    
    # Disconnect
    controller.disconnect()
""")
    
    print("\nApply minimum configuration:")
    print("""
# Apply the minimum necessary configuration
success = controller.apply_minimum_configuration()
if success:
    print("Configuration applied successfully")
""")
    
    print("\nGet comprehensive status:")
    print("""
# Get all parameters at once
status = controller.get_status()
for param, value in status.items():
    print(f"{param}: {value}")
""")


def main():
    """Main demo function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "commands":
            demo_commands()
        elif sys.argv[1] == "python":
            demo_python_usage()
        else:
            print("Usage: python demo.py [commands|python]")
            print("  commands - Show all supported commands")
            print("  python  - Show Python usage examples")
    else:
        demo_basic_usage()


if __name__ == "__main__":
    main()