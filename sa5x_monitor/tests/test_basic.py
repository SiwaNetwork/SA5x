"""
Basic tests for SA5X Monitor
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.config_manager import ConfigManager
from utils.log_parser import LogParser


class TestConfigManager:
    """Test configuration manager"""
    
    def test_config_creation(self):
        """Test configuration manager creation"""
        config = ConfigManager()
        assert config is not None
        assert config.config is not None
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ConfigManager()
        
        # Test serial config
        assert config.get('serial.default_port') == '/dev/ttyS6'
        assert config.get('serial.default_baudrate') == 115200
        assert config.get('serial.default_timeout') == 1.0
        
        # Test monitoring config
        assert config.get('monitoring.default_interval') == 10
        assert config.get('monitoring.log_enabled') is True
        
        # Test holdover test config
        assert config.get('holdover_test.min_duration') == 300
        assert config.get('holdover_test.max_duration') == 86400
        assert config.get('holdover_test.default_duration') == 3600
    
    def test_config_set_get(self):
        """Test setting and getting configuration values"""
        config = ConfigManager()
        
        # Test setting a value
        config.set('test.value', 123)
        assert config.get('test.value') == 123
        
        # Test getting non-existent value
        assert config.get('non.existent', 'default') == 'default'
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = ConfigManager()
        assert config.validate_config() is True


class TestLogParser:
    """Test log parser"""
    
    def test_parser_creation(self):
        """Test log parser creation"""
        parser = LogParser()
        assert parser is not None
        assert len(parser.log_patterns) > 0
    
    def test_parse_line_valid(self):
        """Test parsing valid log line"""
        parser = LogParser()
        
        # Test CSV format
        line = "1234567890.123,1.23e-9,25.5,12.0,0.5,LOCKED"
        result = parser._parse_line(line)
        
        assert result is not None
        assert result['timestamp'] == 1234567890.123
        assert result['frequency_error'] == 1.23e-9
        assert result['temperature'] == 25.5
        assert result['voltage'] == 12.0
        assert result['current'] == 0.5
        assert result['status'] == 'LOCKED'
    
    def test_parse_line_invalid(self):
        """Test parsing invalid log line"""
        parser = LogParser()
        
        # Test invalid line
        line = "invalid,data,format"
        result = parser._parse_line(line)
        
        assert result is None
    
    def test_parse_line_space_separated(self):
        """Test parsing space-separated format"""
        parser = LogParser()
        
        line = "1234567890.123 1.23e-9 25.5 12.0 0.5 LOCKED"
        result = parser._parse_line(line)
        
        assert result is not None
        assert result['timestamp'] == 1234567890.123
        assert result['frequency_error'] == 1.23e-9
        assert result['temperature'] == 25.5


class TestHoldoverTest:
    """Test holdover test functionality"""
    
    def test_test_parameters_validation(self):
        """Test parameter validation"""
        from utils.holdover_test import HoldoverTest
        from utils.config_manager import ConfigManager
        
        config = ConfigManager()
        # Mock controller
        controller = None
        
        test = HoldoverTest(controller, config)
        
        # Test valid parameters
        assert test.min_duration == 300
        assert test.max_duration == 86400
        assert test.min_interval == 1
        assert test.max_interval == 60
    
    def test_calculate_results(self):
        """Test results calculation"""
        from utils.holdover_test import HoldoverTest
        from utils.config_manager import ConfigManager
        import numpy as np
        
        config = ConfigManager()
        test = HoldoverTest(None, config)
        
        # Create mock test data
        test_data = {
            'measurements': [
                {
                    'elapsed_time': 0.0,
                    'frequency_error': 1.0e-9,
                    'temperature': 25.0
                },
                {
                    'elapsed_time': 10.0,
                    'frequency_error': 1.1e-9,
                    'temperature': 25.1
                },
                {
                    'elapsed_time': 20.0,
                    'frequency_error': 1.2e-9,
                    'temperature': 25.2
                }
            ]
        }
        
        results = test._calculate_results(test_data)
        
        assert 'freq_stability' in results
        assert 'temp_stability' in results
        assert 'allan_deviation_1s' in results
        assert 'test_duration' in results
        assert 'measurement_count' in results


class TestSA5XController:
    """Test SA5X controller functionality"""
    
    def test_controller_creation(self):
        """Test controller creation"""
        from utils.sa5x_controller import SA5XController
        
        controller = SA5XController('/dev/ttyS6', 115200, 1.0)
        assert controller is not None
        assert controller.port == '/dev/ttyS6'
        assert controller.baudrate == 115200
        assert controller.timeout == 1.0
    
    def test_status_codes(self):
        """Test status code mapping"""
        from utils.sa5x_controller import SA5XController
        
        controller = SA5XController('/dev/ttyS6')
        
        assert controller.STATUS_CODES[0x00] == 'OK'
        assert controller.STATUS_CODES[0x01] == 'LOCKED'
        assert controller.STATUS_CODES[0x02] == 'HOLDOVER'
        assert controller.STATUS_CODES[0x03] == 'WARMING_UP'
        assert controller.STATUS_CODES[0x04] == 'ERROR'
        assert controller.STATUS_CODES[0x05] == 'NOT_LOCKED'
    
    def test_commands(self):
        """Test command definitions"""
        from utils.sa5x_controller import SA5XController
        
        controller = SA5XController('/dev/ttyS6')
        
        assert 'GET_STATUS' in controller.COMMANDS
        assert 'GET_FREQ_ERROR' in controller.COMMANDS
        assert 'GET_TEMPERATURE' in controller.COMMANDS
        assert 'GET_VOLTAGE' in controller.COMMANDS
        assert 'GET_CURRENT' in controller.COMMANDS
        assert 'GET_LOCK_STATUS' in controller.COMMANDS
        assert 'GET_HOLDOVER_STATUS' in controller.COMMANDS
        assert 'START_HOLDOVER' in controller.COMMANDS
        assert 'STOP_HOLDOVER' in controller.COMMANDS


if __name__ == '__main__':
    pytest.main([__file__])