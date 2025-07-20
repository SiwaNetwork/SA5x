# SA5X Atomic Clock Controller

A Python program for communicating with the Microchip SA5X atomic clock module via serial interface.

## Features

- Serial communication with SA5X module at 57600 baud (default)
- Support for all commands provided in the SA5X datasheet
- Command-line interface with multiple operation modes
- Interactive mode for real-time control
- Comprehensive status monitoring
- Automatic configuration application

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have access to the serial port (typically `/dev/ttyUSB0` on Linux)

## Usage

### Command Line Interface

The main program provides several operation modes:

#### Get Parameter Value
```bash
python sa5x_controller.py --get PpsOffset
```

#### Set Parameter Value
```bash
python sa5x_controller.py --set PpsOffset -30
```

#### Execute Single Command
```bash
python sa5x_controller.py --command "{get,Disciplining}"
```

#### Get Full Status
```bash
python sa5x_controller.py --status
```

#### Apply Minimum Configuration
```bash
python sa5x_controller.py --min-config
```

#### Interactive Mode
```bash
python sa5x_controller.py --interactive
```

### Example Script

Run the example script to see all commands in action:
```bash
python sa5x_examples.py
```

For interactive demo:
```bash
python sa5x_examples.py interactive
```

## Supported Commands

### Minimum Necessary Configuration
The program supports the minimum configuration as specified:

```
{set,Disciplining,1}
{set,PpsWidth,80000000}
{set,TauPps0,10000}
{set,PpsOffset,-30}
{set,DisciplineThresholdPps0,20}
{store}
```

### Get Commands
- `{get,PpsOffset}` - Get PPS offset
- `{get,DisciplineLocked}` - Check if discipline is locked
- `{get,Locked}` - Check if locked
- `{get,Disciplining}` - Get disciplining status
- `{get,Phase}` - Get phase information
- `{get,TauPps0}` - Get Tau for PPS0
- `{get,DigitalTuning}` - Get digital tuning status
- `{get,JamSyncing}` - Get jam syncing status
- `{get,PhaseLimit}` - Get phase limit
- `{get,DisciplineThresholdPps0}` - Get discipline threshold
- `{get,PpsInDetected}` - Check if PPS input detected
- `{get,LockProgress}` - Get lock progress
- `{get,PpsSource}` - Get PPS source
- `{get,LastCorrection}` - Get last correction

### Set Commands
- `{set,PpsOffset,value}` - Set PPS offset
- `{set,PpsWidth,value}` - Set PPS pulse width
- `{set,Disciplining,value}` - Enable/disable disciplining
- `{set,TauPps0,value}` - Set Tau for PPS0
- `{set,PhaseLimit,value}` - Set phase limit
- `{set,DisciplineThresholdPps0,value}` - Set discipline threshold

### Store Command
- `{store}` - Store configuration to flash memory

## Configuration

### Serial Port Settings
- **Default Port**: `/dev/ttyUSB0`
- **Default Baudrate**: 57600
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Timeout**: 1 second

### Custom Port/Baudrate
```bash
python sa5x_controller.py --port /dev/ttyUSB1 --baudrate 115200 --status
```

## Program Structure

### SA5XController Class
The main controller class provides:

- **Connection Management**: `connect()`, `disconnect()`
- **Command Interface**: `send_command()`, `get_parameter()`, `set_parameter()`
- **Configuration**: `store_configuration()`, `apply_minimum_configuration()`
- **Status Monitoring**: `get_status()`
- **Convenience Methods**: `enable_disciplining()`, `set_pps_offset()`, etc.

### Error Handling
- Serial connection errors
- Command timeout handling
- Parameter validation
- Graceful disconnection

## Interactive Mode Commands

When using interactive mode, you can use these commands:

- `get <parameter>` - Get parameter value
- `set <parameter> <value>` - Set parameter value
- `status` - Show all parameters
- `min-config` - Apply minimum configuration
- `store` - Store configuration
- `quit` - Exit

## Examples

### Basic Usage
```python
from sa5x_controller import SA5XController

# Create controller
controller = SA5XController(port="/dev/ttyUSB0", baudrate=57600)

# Connect
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
```

### Apply Minimum Configuration
```python
controller = SA5XController()
if controller.connect():
    success = controller.apply_minimum_configuration()
    if success:
        print("Configuration applied successfully")
    controller.disconnect()
```

## Troubleshooting

### Connection Issues
1. Check if the serial port exists: `ls /dev/ttyUSB*`
2. Verify permissions: `sudo chmod 666 /dev/ttyUSB0`
3. Check if another program is using the port
4. Try different baudrates if needed

### Command Issues
1. Ensure proper command format: `{get,ParameterName}`
2. Check parameter names match SA5X datasheet
3. Verify numeric values are within valid ranges

### Permission Issues
```bash
sudo usermod -a -G dialout $USER
# Then log out and back in
```

## References

- [SA5X User Guide](http://ww1.microchip.com/downloads/en/DeviceDoc/Miniature-Atomic-Clock-MAC-SA5X-Users-Guide-DS50002938A.pdf)
- [Microchip SA5X Product Page](https://www.microchip.com/en-us/product/SA5X)

## License

This program is provided as-is for educational and development purposes.