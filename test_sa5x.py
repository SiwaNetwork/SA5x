#!/usr/bin/env python3
"""
Test script for SA5X controller
Tests the controller functionality without requiring actual hardware.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sa5x_controller import SA5XController


class TestSA5XController(unittest.TestCase):
    """Test cases for SA5XController class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.controller = SA5XController(port="/dev/ttyUSB0", baudrate=57600)
    
    @patch('serial.Serial')
    def test_connect_success(self, mock_serial):
        """Test successful connection"""
        mock_serial.return_value.is_open = True
        
        result = self.controller.connect()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.controller.serial_conn)
        mock_serial.assert_called_once()
    
    @patch('serial.Serial')
    def test_connect_failure(self, mock_serial):
        """Test connection failure"""
        mock_serial.side_effect = Exception("Connection failed")
        
        result = self.controller.connect()
        
        self.assertFalse(result)
        self.assertIsNone(self.controller.serial_conn)
    
    @patch('serial.Serial')
    def test_send_command(self, mock_serial):
        """Test sending commands"""
        # Mock serial connection
        mock_conn = MagicMock()
        mock_conn.is_open = True
        mock_conn.write.return_value = None
        mock_conn.readline.return_value = b"OK\r\n"
        mock_serial.return_value = mock_conn
        
        self.controller.connect()
        
        # Test command sending
        response = self.controller.send_command("{get,PpsOffset}")
        
        self.assertEqual(response, "OK")
        mock_conn.write.assert_called_once_with(b"{get,PpsOffset}\r\n")
    
    @patch('serial.Serial')
    def test_get_parameter(self, mock_serial):
        """Test getting parameters"""
        # Mock serial connection
        mock_conn = MagicMock()
        mock_conn.is_open = True
        mock_conn.write.return_value = None
        mock_conn.readline.return_value = b"-30\r\n"
        mock_serial.return_value = mock_conn
        
        self.controller.connect()
        
        # Test parameter getting
        response = self.controller.get_parameter("PpsOffset")
        
        self.assertEqual(response, "-30")
        mock_conn.write.assert_called_once_with(b"{get,PpsOffset}\r\n")
    
    @patch('serial.Serial')
    def test_set_parameter(self, mock_serial):
        """Test setting parameters"""
        # Mock serial connection
        mock_conn = MagicMock()
        mock_conn.is_open = True
        mock_conn.write.return_value = None
        mock_conn.readline.return_value = b"OK\r\n"
        mock_serial.return_value = mock_conn
        
        self.controller.connect()
        
        # Test parameter setting
        response = self.controller.set_parameter("PpsOffset", -30)
        
        self.assertEqual(response, "OK")
        mock_conn.write.assert_called_once_with(b"{set,PpsOffset,-30}\r\n")
    
    @patch('serial.Serial')
    def test_store_configuration(self, mock_serial):
        """Test storing configuration"""
        # Mock serial connection
        mock_conn = MagicMock()
        mock_conn.is_open = True
        mock_conn.write.return_value = None
        mock_conn.readline.return_value = b"Stored\r\n"
        mock_serial.return_value = mock_conn
        
        self.controller.connect()
        
        # Test configuration storage
        response = self.controller.store_configuration()
        
        self.assertEqual(response, "Stored")
        mock_conn.write.assert_called_once_with(b"{store}\r\n")
    
    @patch('serial.Serial')
    def test_apply_minimum_configuration(self, mock_serial):
        """Test applying minimum configuration"""
        # Mock serial connection
        mock_conn = MagicMock()
        mock_conn.is_open = True
        mock_conn.write.return_value = None
        mock_conn.readline.return_value = b"OK\r\n"
        mock_serial.return_value = mock_conn
        
        self.controller.connect()
        
        # Test minimum configuration
        success = self.controller.apply_minimum_configuration()
        
        self.assertTrue(success)
        # Should have called write 6 times (5 set commands + 1 store)
        self.assertEqual(mock_conn.write.call_count, 6)
    
    @patch('serial.Serial')
    def test_get_status(self, mock_serial):
        """Test getting comprehensive status"""
        # Mock serial connection
        mock_conn = MagicMock()
        mock_conn.is_open = True
        mock_conn.write.return_value = None
        mock_conn.readline.return_value = b"1\r\n"  # All parameters return 1
        mock_serial.return_value = mock_conn
        
        self.controller.connect()
        
        # Test status getting
        status = self.controller.get_status()
        
        # Should have 14 parameters
        self.assertEqual(len(status), 14)
        # All values should be "1"
        for value in status.values():
            self.assertEqual(value, "1")


class TestCommandFormat(unittest.TestCase):
    """Test command format validation"""
    
    def test_command_format(self):
        """Test that commands are formatted correctly"""
        controller = SA5XController()
        
        # Test get command format
        with patch.object(controller, 'send_command') as mock_send:
            controller.get_parameter("PpsOffset")
            mock_send.assert_called_once_with("{get,PpsOffset}")
        
        # Test set command format
        with patch.object(controller, 'send_command') as mock_send:
            controller.set_parameter("PpsOffset", -30)
            mock_send.assert_called_once_with("{set,PpsOffset,-30}")
        
        # Test store command format
        with patch.object(controller, 'send_command') as mock_send:
            controller.store_configuration()
            mock_send.assert_called_once_with("{store}")


def run_tests():
    """Run all tests"""
    print("Running SA5X Controller Tests...")
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()