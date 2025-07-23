# SA5X Rubidium Generator Monitor

A comprehensive monitoring and testing suite for SA5X Rubidium frequency generators, providing both command-line and web-based interfaces for real-time monitoring, holdover testing, and data analysis.

## Features

- **Real-time Monitoring**: Track generator status, frequency stability, and temperature
- **Holdover Testing**: Automated testing with configurable duration and intervals
- **Data Logging**: Comprehensive logging with CSV export capabilities
- **Web Interface**: Real-time web dashboard with live charts and status updates
- **Command-line Interface**: Full-featured CLI for automation and scripting
- **Log Analysis**: Parse and analyze existing test logs with statistical metrics

## Installation

### Prerequisites

- Python 3.8 or higher
- Serial port access (typically `/dev/ttyS6` for SA5X)
- Linux/Unix environment (tested on Ubuntu)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd sa5x_monitor
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Verify installation:
```bash
python test_setup.py
```

## Configuration

The default configuration is stored in `config/sa5x_config.json`:

```json
{
    "serial": {
        "default_port": "/dev/ttyS6",
        "baudrate": 115200,
        "timeout": 1.0
    },
    "monitoring": {
        "default_interval": 10,
        "buffer_size": 1000
    },
    "holdover_test": {
        "default_duration": 3600,
        "warmup_time": 300,
        "measurement_interval": 10
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "web": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": false
    }
}
```

## Usage

### Command-Line Interface

#### Basic Monitoring
```bash
# Start continuous monitoring with default port
python run_cli.py --monitor

# Specify a different port
python run_cli.py --port /dev/ttyUSB0 --monitor

# Enable verbose logging
python run_cli.py --monitor --verbose
```

#### Holdover Testing
```bash
# Run a 1-hour holdover test
python run_cli.py --holdover-test --duration 3600

# Run with custom interval and output file
python run_cli.py --holdover-test --duration 7200 --interval 5 --output results.csv
```

#### Log Analysis
```bash
# Parse an existing holdover log
python run_cli.py --parse-log holdover_20240723_170000.log
```

#### Help and Options
```bash
python run_cli.py --help
```

### Web Interface

1. Start the web server:
```bash
python run_web.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Features available in the web interface:
   - Real-time status dashboard
   - Live frequency and temperature charts
   - Holdover test control and monitoring
   - Historical data viewing
   - Log file download

## API Endpoints

The web interface provides several REST API endpoints:

- `GET /api/status` - Current generator status
- `GET /api/history` - Historical data (last 1000 points)
- `POST /api/start_holdover` - Start holdover test
- `POST /api/stop_holdover` - Stop holdover test
- `GET /api/holdover_status` - Current holdover test status
- `GET /api/logs` - List available log files
- `GET /api/download_log/<filename>` - Download specific log file

## Data Format

### Status Response
```json
{
    "timestamp": "2024-07-23 17:00:00",
    "lock_status": "LOCKED",
    "frequency_offset": 1.234e-10,
    "temperature": 45.67,
    "voltage": 12.34,
    "current": 0.567,
    "alarm_status": "NONE"
}
```

### Holdover Test Results
```json
{
    "duration": 3600,
    "frequency_stability": 1.23e-11,
    "allan_deviation": 4.56e-12,
    "temperature_stability": 0.123,
    "total_measurements": 360
}
```

## Troubleshooting

### Common Issues

1. **Serial Port Access Denied**
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and back in for changes to take effect
   ```

2. **Port Not Found**
   - Check available ports: `ls /dev/tty*`
   - Verify SA5X connection and power
   - Try different USB ports if using USB-to-serial adapter

3. **Module Import Errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Web Interface Not Loading**
   - Check if port 5000 is available: `sudo lsof -i :5000`
   - Try a different port in the configuration
   - Check firewall settings

## Development

### Project Structure
```
sa5x_monitor/
├── cli/                    # Command-line interface modules
│   └── main.py
├── config/                 # Configuration files
│   └── sa5x_config.json
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── config_manager.py
│   ├── holdover_test.py
│   ├── log_parser.py
│   └── sa5x_controller.py
├── web/                    # Web interface modules
│   ├── app.py
│   ├── static/            # CSS, JS files
│   └── templates/         # HTML templates
├── logs/                   # Log file directory
├── requirements.txt        # Python dependencies
├── run_cli.py             # CLI entry point
├── run_web.py             # Web server entry point
└── test_setup.py          # Setup verification script
```

### Adding New Features

1. Create new modules in appropriate directories
2. Update `__init__.py` files for imports
3. Add configuration options to `sa5x_config.json`
4. Update documentation and help text

## License

[Your License Here]

## Contributing

[Contributing Guidelines]

## Support

For issues and questions:
- Check the troubleshooting section
- Review existing issues on GitHub
- Contact support at [support email]