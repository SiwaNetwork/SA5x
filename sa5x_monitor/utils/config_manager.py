"""
Configuration Manager for SA5X Monitor
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Configuration manager for SA5X monitor"""
    
    def __init__(self, config_file: str = 'config/sa5x_config.json'):
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        self.config = self._load_default_config()
        
        if self.config_file.exists():
            self._load_config()
        else:
            self._save_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'serial': {
                'default_port': '/dev/ttyUSB0',
                'default_baudrate': 115200,
                'default_timeout': 1.0,
                'retry_attempts': 3,
                'retry_delay': 1.0
            },
            'monitoring': {
                'default_interval': 10,
                'max_interval': 3600,
                'min_interval': 1,
                'log_enabled': True,
                'log_level': 'INFO'
            },
            'holdover_test': {
                'min_duration': 300,
                'max_duration': 86400,
                'default_duration': 3600,
                'min_interval': 1,
                'max_interval': 60,
                'default_interval': 10,
                'auto_start_holdover': True,
                'auto_stop_holdover': True
            },
            'analysis': {
                'allan_deviation_taus': [1, 10, 100, 1000],
                'frequency_stability_threshold': 1e-9,
                'temperature_stability_threshold': 0.1,
                'enable_advanced_analysis': True
            },
            'output': {
                'default_output_dir': 'results',
                'save_json': True,
                'save_summary': True,
                'save_plots': True,
                'timestamp_format': '%Y%m%d_%H%M%S'
            },
            'web_interface': {
                'host': 'localhost',
                'port': 8080,
                'debug': False,
                'auto_reload': True,
                'max_connections': 10
            },
            'alerts': {
                'enable_alerts': True,
                'frequency_error_threshold': 1e-8,
                'temperature_threshold': 50.0,
                'voltage_threshold': 15.0,
                'current_threshold': 2.0,
                'status_alerts': ['ERROR', 'NOT_LOCKED']
            },
            'logging': {
                'log_file': 'sa5x_monitor.log',
                'max_log_size': 10485760,  # 10MB
                'backup_count': 5,
                'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)
            
            # Merge with default config
            self._merge_config(file_config)
            self.logger.info(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.logger.info("Using default configuration")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing config"""
        def merge_dicts(base, update):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value
        
        merge_dicts(self.config, new_config)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by key path (e.g., 'serial.default_port')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value by key path"""
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        self._save_config()
    
    def get_serial_config(self) -> Dict[str, Any]:
        """Get serial configuration"""
        return self.config['serial']
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return self.config['monitoring']
    
    def get_holdover_test_config(self) -> Dict[str, Any]:
        """Get holdover test configuration"""
        return self.config['holdover_test']
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration"""
        return self.config['analysis']
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration"""
        return self.config['output']
    
    def get_web_config(self) -> Dict[str, Any]:
        """Get web interface configuration"""
        return self.config['web_interface']
    
    def get_alerts_config(self) -> Dict[str, Any]:
        """Get alerts configuration"""
        return self.config['alerts']
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config['logging']
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        try:
            # Validate serial config
            serial_config = self.config['serial']
            assert isinstance(serial_config['default_baudrate'], int)
            assert isinstance(serial_config['default_timeout'], (int, float))
            assert isinstance(serial_config['retry_attempts'], int)
            
            # Validate monitoring config
            monitoring_config = self.config['monitoring']
            assert isinstance(monitoring_config['default_interval'], int)
            assert monitoring_config['default_interval'] > 0
            
            # Validate holdover test config
            holdover_config = self.config['holdover_test']
            assert holdover_config['min_duration'] < holdover_config['max_duration']
            assert holdover_config['min_interval'] < holdover_config['max_interval']
            
            return True
            
        except (KeyError, AssertionError) as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self._load_default_config()
        self._save_config()
        self.logger.info("Configuration reset to defaults")
    
    def export_config(self, output_file: str):
        """Export configuration to file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info(f"Configuration exported to {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
    
    def import_config(self, input_file: str):
        """Import configuration from file"""
        try:
            with open(input_file, 'r') as f:
                new_config = json.load(f)
            
            self._merge_config(new_config)
            self._save_config()
            self.logger.info(f"Configuration imported from {input_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            'config_file': str(self.config_file),
            'serial_port': self.get('serial.default_port'),
            'monitoring_interval': self.get('monitoring.default_interval'),
            'holdover_duration': self.get('holdover_test.default_duration'),
            'web_host': self.get('web_interface.host'),
            'web_port': self.get('web_interface.port'),
            'alerts_enabled': self.get('alerts.enable_alerts'),
            'log_level': self.get('logging.log_level')
        }