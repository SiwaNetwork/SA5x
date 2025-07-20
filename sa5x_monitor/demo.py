#!/usr/bin/env python3
"""
SA5X Monitor Demo - Version without external dependencies
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

class SimpleLogParser:
    """Simple log parser without numpy dependency"""
    
    def __init__(self):
        self.log_patterns = [
            r'^(\d+\.?\d*),([+-]?\d+\.?\d*e?[+-]?\d*),([+-]?\d+\.?\d*),([+-]?\d+\.?\d*),([+-]?\d+\.?\d*),(\w+)$',
            r'^(\d+\.?\d*)\s+([+-]?\d+\.?\d*e?[+-]?\d*)\s+([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+(\w+)$'
        ]
    
    def parse_log_file(self, log_file):
        """Parse log file and return measurements"""
        measurements = []
        
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                measurement = self._parse_line(line)
                if measurement:
                    measurements.append(measurement)
                else:
                    print(f"Warning: Could not parse line {line_num}: {line}")
        
        return measurements
    
    def _parse_line(self, line):
        """Parse a single log line"""
        for pattern in self.log_patterns:
            match = re.match(pattern, line)
            if match:
                try:
                    return {
                        'timestamp': float(match.group(1)),
                        'frequency_error': float(match.group(2)),
                        'temperature': float(match.group(3)),
                        'voltage': float(match.group(4)),
                        'current': float(match.group(5)),
                        'status': match.group(6)
                    }
                except (ValueError, IndexError) as e:
                    print(f"Error parsing values: {e}")
                    continue
        return None
    
    def analyze_measurements(self, measurements):
        """Analyze measurement data"""
        if len(measurements) < 2:
            return None
        
        # Extract data
        timestamps = [m['timestamp'] for m in measurements]
        freq_errors = [m['frequency_error'] for m in measurements]
        temperatures = [m['temperature'] for m in measurements]
        voltages = [m['voltage'] for m in measurements]
        currents = [m['current'] for m in measurements]
        
        # Calculate basic statistics
        duration = timestamps[-1] - timestamps[0]
        
        # Simple statistics without numpy
        freq_mean = sum(freq_errors) / len(freq_errors)
        freq_variance = sum((x - freq_mean) ** 2 for x in freq_errors) / len(freq_errors)
        freq_stability = freq_variance ** 0.5
        
        temp_mean = sum(temperatures) / len(temperatures)
        temp_variance = sum((x - temp_mean) ** 2 for x in temperatures) / len(temperatures)
        temp_stability = temp_variance ** 0.5
        
        # Status analysis
        status_counts = {}
        for m in measurements:
            status = m['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'duration': duration,
            'measurement_count': len(measurements),
            'freq_stability': freq_stability,
            'freq_error_min': min(freq_errors),
            'freq_error_max': max(freq_errors),
            'freq_error_mean': freq_mean,
            'temp_stability': temp_stability,
            'temp_min': min(temperatures),
            'temp_max': max(temperatures),
            'temp_mean': temp_mean,
            'voltage_min': min(voltages),
            'voltage_max': max(voltages),
            'voltage_mean': sum(voltages) / len(voltages),
            'current_min': min(currents),
            'current_max': max(currents),
            'current_mean': sum(currents) / len(currents),
            'status_distribution': status_counts,
            'primary_status': max(status_counts.items(), key=lambda x: x[1])[0] if status_counts else 'UNKNOWN'
        }

def demo_parser():
    """Demo log parser functionality"""
    print("SA5X Monitor - Log Parser Demo")
    print("=" * 40)
    
    # Test with example log
    example_file = Path('examples/sample_holdover_log.txt')
    if not example_file.exists():
        print("❌ Example log file not found")
        return False
    
    try:
        parser = SimpleLogParser()
        measurements = parser.parse_log_file(str(example_file))
        
        if not measurements:
            print("❌ No measurements found in log file")
            return False
        
        print(f"✓ Parsed {len(measurements)} measurements")
        
        # Analyze measurements
        results = parser.analyze_measurements(measurements)
        
        if results:
            print("\nAnalysis Results:")
            print(f"  Duration: {results['duration']:.2f} seconds")
            print(f"  Measurements: {results['measurement_count']}")
            print(f"  Frequency Stability: {results['freq_stability']:.2e}")
            print(f"  Temperature Stability: {results['temp_stability']:.3f}°C")
            print(f"  Temperature Range: {results['temp_min']:.2f}°C - {results['temp_max']:.2f}°C")
            print(f"  Voltage Range: {results['voltage_min']:.2f}V - {results['voltage_max']:.2f}V")
            print(f"  Current Range: {results['current_min']:.3f}A - {results['current_max']:.3f}A")
            print(f"  Primary Status: {results['primary_status']}")
            
            print("\nStatus Distribution:")
            for status, count in results['status_distribution'].items():
                percentage = (count / results['measurement_count']) * 100
                print(f"  {status}: {count} ({percentage:.1f}%)")
            
            print("\n🎉 Demo completed successfully!")
            return True
        else:
            print("❌ Failed to analyze measurements")
            return False
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_config():
    """Demo configuration functionality"""
    print("\nSA5X Monitor - Configuration Demo")
    print("=" * 40)
    
    # Load default config
    config_file = Path('config/sa5x_config.json')
    if not config_file.exists():
        print("❌ Config file not found")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("Configuration loaded successfully:")
        print(f"  Serial Port: {config['serial']['default_port']}")
        print(f"  Baudrate: {config['serial']['default_baudrate']}")
        print(f"  Monitoring Interval: {config['monitoring']['default_interval']}s")
        print(f"  Holdover Duration: {config['holdover_test']['default_duration']}s")
        print(f"  Web Host: {config['web_interface']['host']}")
        print(f"  Web Port: {config['web_interface']['port']}")
        
        print("✓ Configuration demo completed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration demo failed: {e}")
        return False

def show_usage():
    """Show usage examples"""
    print("\nSA5X Monitor - Usage Examples")
    print("=" * 40)
    
    print("CLI Usage:")
    print("  python run_cli.py --port /dev/ttyUSB0")
    print("  python run_cli.py --port /dev/ttyUSB0 --monitor --interval 10")
    print("  python run_cli.py --port /dev/ttyUSB0 --holdover-test --duration 3600")
    print("  python run_cli.py --parse-log examples/sample_holdover_log.txt")
    
    print("\nWeb Usage:")
    print("  python run_web.py")
    print("  python run_web.py --host 0.0.0.0 --port 8080")
    
    print("\nInstallation:")
    print("  pip install -r requirements.txt")
    print("  python simple_test.py")

def main():
    """Main demo function"""
    print("SA5X Rubidium Generator Monitor")
    print("Based on Time-Card project and Timetickler")
    print("=" * 50)
    
    demos = [
        demo_parser,
        demo_config
    ]
    
    passed = 0
    total = len(demos)
    
    for demo in demos:
        if demo():
            passed += 1
    
    show_usage()
    
    print(f"\nDemo Results: {passed}/{total} demos completed")
    
    if passed == total:
        print("🎉 All demos completed successfully!")
        print("\nThe SA5X Monitor is ready to use!")
        print("Install dependencies with: pip install -r requirements.txt")
        return True
    else:
        print("❌ Some demos failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)