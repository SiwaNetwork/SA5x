#!/usr/bin/env python3
"""
SA5X Rubidium Generator Monitor - CLI Version
Based on Time-Card project and Timetickler
"""

import argparse
import sys
import time
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.sa5x_controller import SA5XController
from utils.holdover_test import HoldoverTest
from utils.log_parser import LogParser
from utils.config_manager import ConfigManager


def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('sa5x_monitor.log')
        ]
    )


def main():
    parser = argparse.ArgumentParser(
        description='SA5X Rubidium Generator Monitor and Test Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --port /dev/ttyS6 --monitor
  %(prog)s --port /dev/ttyS6 --holdover-test --duration 3600
  %(prog)s --parse-log holdover_log.txt
        """
    )
    
    parser.add_argument('--port', '-p', 
                       help='Serial port for SA5X communication')
    parser.add_argument('--baudrate', '-b', type=int, default=115200,
                       help='Baud rate (default: 115200)')
    parser.add_argument('--timeout', '-t', type=float, default=1.0,
                       help='Serial timeout in seconds (default: 1.0)')
    
    # Operation modes
    parser.add_argument('--monitor', action='store_true',
                       help='Start continuous monitoring')
    parser.add_argument('--holdover-test', action='store_true',
                       help='Run holdover test')
    parser.add_argument('--parse-log', metavar='FILE',
                       help='Parse existing holdover log file')
    
    # Test parameters
    parser.add_argument('--duration', type=int, default=3600,
                       help='Test duration in seconds (default: 3600)')
    parser.add_argument('--interval', type=int, default=10,
                       help='Measurement interval in seconds (default: 10)')
    parser.add_argument('--output', '-o', default='holdover_results.txt',
                       help='Output file for test results')
    
    # General options
    parser.add_argument('--config', '-c', default='config/sa5x_config.json',
                       help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = ConfigManager(args.config)
        
        if args.parse_log:
            # Parse existing log file
            parser = LogParser()
            results = parser.parse_holdover_log(args.parse_log)
            print("Holdover Test Results:")
            print(f"Duration: {results['duration']:.2f} seconds")
            print(f"Frequency Stability: {results['freq_stability']:.2e}")
            print(f"Allan Deviation: {results['allan_deviation']:.2e}")
            print(f"Temperature Stability: {results['temp_stability']:.3f}°C")
            return
        
        if not args.port:
            logger.error("Serial port is required for monitoring and testing")
            sys.exit(1)
        
        # Initialize SA5X controller
        controller = SA5XController(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout
        )
        
        if args.holdover_test:
            # Run holdover test
            test = HoldoverTest(controller, config)
            logger.info(f"Starting holdover test for {args.duration} seconds")
            results = test.run_test(
                duration=args.duration,
                interval=args.interval,
                output_file=args.output
            )
            print(f"Holdover test completed. Results saved to {args.output}")
            
        elif args.monitor:
            # Start continuous monitoring
            logger.info("Starting continuous monitoring")
            try:
                while True:
                    status = controller.get_status()
                    freq_error = controller.get_frequency_error()
                    temperature = controller.get_temperature()
                    
                    print(f"\rStatus: {status}, Freq Error: {freq_error:.2e}, Temp: {temperature:.2f}°C", 
                          end='', flush=True)
                    
                    time.sleep(args.interval)
                    
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                
        else:
            # Default: show current status
            status = controller.get_status()
            freq_error = controller.get_frequency_error()
            temperature = controller.get_temperature()
            
            print("SA5X Current Status:")
            print(f"Status: {status}")
            print(f"Frequency Error: {freq_error:.2e}")
            print(f"Temperature: {temperature:.2f}°C")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()