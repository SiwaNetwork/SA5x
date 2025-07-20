#!/usr/bin/env python3
"""
Simple test for SA5X Monitor components
"""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_config_manager():
    """Test configuration manager"""
    print("Testing ConfigManager...")
    
    try:
        from utils.config_manager import ConfigManager
        
        config = ConfigManager()
        
        # Test basic functionality
        assert config is not None
        assert config.get('serial.default_port') == '/dev/ttyUSB0'
        assert config.get('serial.default_baudrate') == 115200
        
        # Test setting values
        config.set('test.value', 123)
        assert config.get('test.value') == 123
        
        print("✓ ConfigManager test passed")
        return True
        
    except Exception as e:
        print(f"✗ ConfigManager test failed: {e}")
        return False

def test_log_parser_basic():
    """Test basic log parser functionality"""
    print("Testing LogParser basic functionality...")
    
    try:
        from utils.log_parser import LogParser
        
        parser = LogParser()
        
        # Test line parsing
        test_line = "1234567890.123,1.23e-9,25.5,12.0,0.5,LOCKED"
        result = parser._parse_line(test_line)
        
        if result:
            assert result['timestamp'] == 1234567890.123
            assert result['frequency_error'] == 1.23e-9
            assert result['temperature'] == 25.5
            assert result['voltage'] == 12.0
            assert result['current'] == 0.5
            assert result['status'] == 'LOCKED'
            print("✓ LogParser basic test passed")
            return True
        else:
            print("✗ LogParser basic test failed: could not parse line")
            return False
            
    except Exception as e:
        print(f"✗ LogParser basic test failed: {e}")
        return False

def test_sample_log():
    """Test parsing sample log file"""
    print("Testing sample log parsing...")
    
    try:
        # Create sample log
        sample_log = """# Sample holdover test log file
# Format: timestamp,frequency_error,temperature,voltage,current,status
1701234567.123,1.23e-9,25.5,12.0,0.5,LOCKED
1701234567.133,1.25e-9,25.6,12.0,0.5,LOCKED
1701234567.143,1.22e-9,25.4,12.0,0.5,LOCKED
1701234567.153,1.24e-9,25.5,12.0,0.5,LOCKED
1701234567.163,1.21e-9,25.3,12.0,0.5,LOCKED"""
        
        with open('test_sample.log', 'w') as f:
            f.write(sample_log)
        
        # Test parsing
        from utils.log_parser import LogParser
        parser = LogParser()
        
        # Parse the file
        measurements = parser._parse_log_file('test_sample.log')
        
        assert len(measurements) == 5
        assert measurements[0]['timestamp'] == 1701234567.123
        assert measurements[0]['status'] == 'LOCKED'
        
        print("✓ Sample log parsing test passed")
        return True
        
    except Exception as e:
        print(f"✗ Sample log parsing test failed: {e}")
        return False
    
    finally:
        # Clean up
        if Path('test_sample.log').exists():
            Path('test_sample.log').unlink()

def test_existing_log():
    """Test parsing existing example log"""
    print("Testing existing example log...")
    
    try:
        example_file = Path('examples/sample_holdover_log.txt')
        if not example_file.exists():
            print("✗ Example log file not found")
            return False
        
        from utils.log_parser import LogParser
        parser = LogParser()
        
        # Parse the example file
        measurements = parser._parse_log_file(str(example_file))
        
        assert len(measurements) > 0
        print(f"✓ Parsed {len(measurements)} measurements from example log")
        return True
        
    except Exception as e:
        print(f"✗ Existing log test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("SA5X Monitor - Simple Tests")
    print("=" * 40)
    
    tests = [
        test_config_manager,
        test_log_parser_basic,
        test_sample_log,
        test_existing_log
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)