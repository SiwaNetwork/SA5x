#!/usr/bin/env python3
"""
SA5X Command Examples
Demonstrates all the commands provided by the user for the SA5X atomic clock module.
"""

from sa5x_controller import SA5XController
import time


def run_examples():
    """Run all the example commands provided by the user"""
    
    # Initialize controller
    controller = SA5XController()
    
    if not controller.connect():
        print("Failed to connect to SA5X module")
        return
    
    try:
        print("=== SA5X Command Examples ===\n")
        
        # Minimum necessary configuration
        print("1. Applying minimum necessary configuration:")
        print("   {set,Disciplining,1}")
        print("   {set,PpsWidth,80000000}")
        print("   {set,TauPps0,10000}")
        print("   {set,PpsOffset,-30}")
        print("   {set,DisciplineThresholdPps0,20}")
        print("   {store}")
        
        success = controller.apply_minimum_configuration()
        print(f"   Result: {'Success' if success else 'Failed'}\n")
        
        # Individual command examples
        print("2. Individual command examples:")
        
        # Get commands
        get_commands = [
            "PpsOffset",
            "DisciplineLocked", 
            "Locked",
            "Disciplining",
            "Phase",
            "TauPps0",
            "DigitalTuning",
            "JamSyncing",
            "PhaseLimit",
            "DisciplineThresholdPps0",
            "PpsInDetected",
            "LockProgress",
            "PpsSource",
            "LastCorrection"
        ]
        
        for param in get_commands:
            response = controller.get_parameter(param)
            print(f"   {{get,{param}}} -> {response}")
        
        print()
        
        # Set commands
        set_commands = [
            ("PpsOffset", 0),
            ("PpsWidth", 80000000),
            ("Disciplining", 1),
            ("TauPps0", 1000),
            ("TauPps0", 500),
            ("TauPps0", 100),
            ("TauPps0", 10),
            ("PhaseLimit", 1000),
            ("PpsOffset", -10)
        ]
        
        for param, value in set_commands:
            response = controller.set_parameter(param, value)
            print(f"   {{set,{param},{value}}} -> {response}")
        
        print()
        
        # Store configuration
        print("3. Storing configuration:")
        store_response = controller.store_configuration()
        print(f"   {{store}} -> {store_response}")
        
        print()
        
        # Get comprehensive status
        print("4. Current status:")
        status = controller.get_status()
        for param, value in status.items():
            print(f"   {param}: {value}")
            
    finally:
        controller.disconnect()


def interactive_demo():
    """Interactive demonstration of SA5X commands"""
    
    controller = SA5XController()
    
    if not controller.connect():
        print("Failed to connect to SA5X module")
        return
    
    try:
        print("=== SA5X Interactive Demo ===")
        print("Available commands:")
        print("  get <param> - Get parameter value")
        print("  set <param> <value> - Set parameter value")
        print("  status - Show all parameters")
        print("  min-config - Apply minimum configuration")
        print("  store - Store configuration")
        print("  quit - Exit")
        print()
        
        while True:
            try:
                command = input("SA5X> ").strip().split()
                
                if not command:
                    continue
                    
                if command[0].lower() == 'quit':
                    break
                elif command[0].lower() == 'get' and len(command) == 2:
                    response = controller.get_parameter(command[1])
                    print(f"{command[1]}: {response}")
                elif command[0].lower() == 'set' and len(command) == 3:
                    response = controller.set_parameter(command[1], command[2])
                    print(f"Set {command[1]} = {command[2]}")
                    print(f"Response: {response}")
                elif command[0].lower() == 'status':
                    status = controller.get_status()
                    for param, value in status.items():
                        print(f"  {param}: {value}")
                elif command[0].lower() == 'min-config':
                    success = controller.apply_minimum_configuration()
                    print(f"Minimum config: {'Success' if success else 'Failed'}")
                elif command[0].lower() == 'store':
                    response = controller.store_configuration()
                    print(f"Store: {response}")
                else:
                    print("Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                break
                
    finally:
        controller.disconnect()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_demo()
    else:
        run_examples()