#!/usr/bin/env python3
"""
Simple test for log parser without external dependencies
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Mock serial module for testing
class MockSerial:
    def __init__(self, *args, **kwargs):
        pass
    
    def is_open(self):
        return True
    
    def close(self):
        pass

# Mock numpy for testing
class MockNumpy:
    @staticmethod
    def array(data):
        return data
    
    @staticmethod
    def std(data):
        return 0.001
    
    @staticmethod
    def polyfit(x, y, degree):
        return [0.0, 0.0]
    
    @staticmethod
    def min(data):
        return min(data)
    
    @staticmethod
    def max(data):
        return max(data)
    
    @staticmethod
    def mean(data):
        return sum(data) / len(data)
    
    @staticmethod
    def diff(data):
        return [data[i+1] - data[i] for i in range(len(data)-1)]
    
    @staticmethod
    def sqrt(value):
        return value ** 0.5

# Mock the modules
sys.modules['serial'] = type('MockSerialModule', (), {'Serial': MockSerial})()
sys.modules['numpy'] = MockNumpy()

from utils.log_parser import LogParser

def test_parser():
    """Test the log parser with sample data"""
    
    # Create sample log content
    sample_log = """# Sample holdover test log file
# Format: timestamp,frequency_error,temperature,voltage,current,status
1701234567.123,1.23e-9,25.5,12.0,0.5,LOCKED
1701234567.133,1.25e-9,25.6,12.0,0.5,LOCKED
1701234567.143,1.22e-9,25.4,12.0,0.5,LOCKED
1701234567.153,1.24e-9,25.5,12.0,0.5,LOCKED
1701234567.163,1.21e-9,25.3,12.0,0.5,LOCKED
1701234567.173,1.26e-9,25.7,12.0,0.5,LOCKED
1701234567.183,1.23e-9,25.5,12.0,0.5,LOCKED
1701234567.193,1.25e-9,25.6,12.0,0.5,LOCKED
1701234567.203,1.22e-9,25.4,12.0,0.5,LOCKED
1701234567.213,1.24e-9,25.5,12.0,0.5,LOCKED"""
    
    # Write sample log to file
    with open('test_log.txt', 'w') as f:
        f.write(sample_log)
    
    try:
        # Test parser
        parser = LogParser()
        results = parser.parse_holdover_log('test_log.txt')
        
        print("Log Parser Test Results:")
        print("=" * 40)
        print(f"Duration: {results['duration']:.2f} seconds")
        print(f"Measurement Count: {results['measurement_count']}")
        print(f"Frequency Stability: {results['freq_stability']:.2e}")
        print(f"Allan Deviation: {results['allan_deviation']:.2e}")
        print(f"Temperature Stability: {results['temp_stability']:.3f}°C")
        print(f"Temperature Range: {results['temp_min']:.2f}°C - {results['temp_max']:.2f}°C")
        print(f"Voltage Range: {results['voltage_min']:.2f}V - {results['voltage_max']:.2f}V")
        print(f"Current Range: {results['current_min']:.3f}A - {results['current_max']:.3f}A")
        print(f"Primary Status: {results['primary_status']}")
        
        print("\nStatus Distribution:")
        for status, count in results['status_distribution'].items():
            percentage = (count / results['measurement_count']) * 100
            print(f"  {status}: {count} ({percentage:.1f}%)")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    
    finally:
        # Clean up
        if Path('test_log.txt').exists():
            Path('test_log.txt').unlink()

if __name__ == '__main__':
    success = test_parser()
    sys.exit(0 if success else 1)