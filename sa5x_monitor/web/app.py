#!/usr/bin/env python3
"""
SA5X Web Monitor - Flask Application
"""

import os
import sys
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from utils.sa5x_controller import SA5XController
from utils.holdover_test import HoldoverTest
from utils.log_parser import LogParser
from utils.config_manager import ConfigManager


class SA5XWebMonitor:
    """Web monitor for SA5X"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'sa5x_monitor_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize components
        self.config = ConfigManager()
        self.controller = None
        self.monitoring_thread = None
        self.monitoring_active = False
        self.current_data = {}
        
        # Добавляем переменные для хранения загруженных данных
        self.uploaded_log_data = None
        self.uploaded_log_results = None
        
        # Setup logging
        self._setup_logging()
        
        # Setup routes
        self._setup_routes()
        
        # Setup socket events
        self._setup_socket_events()
    
    def _setup_logging(self):
        """Setup logging for web application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sa5x_web_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('index.html')
        
        @self.app.route('/status')
        def status():
            """Get current SA5X status"""
            if self.controller:
                try:
                    data = self.controller.get_all_parameters()
                    data['timestamp'] = datetime.now().isoformat()
                    return jsonify(data)
                except Exception as e:
                    self.logger.error(f"Failed to get status: {e}")
                    return jsonify({'error': str(e)}), 500
            else:
                return jsonify({'error': 'Controller not connected'}), 503
        
        @self.app.route('/connect', methods=['POST'])
        def connect():
            """Connect to SA5X"""
            try:
                data = request.get_json()
                port = data.get('port', '/dev/ttyS6')
                baudrate = data.get('baudrate', 115200)
                timeout = data.get('timeout', 1.0)
                
                # Check if port exists before trying to connect
                import os
                if not os.path.exists(port):
                    error_msg = f"Serial port {port} does not exist. Available ports: "
                    # List available serial ports
                    import glob
                    available_ports = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
                    if available_ports:
                        error_msg += ", ".join(available_ports)
                    else:
                        error_msg += "none found"
                    return jsonify({'error': error_msg}), 400
                
                self.controller = SA5XController(port, baudrate, timeout)
                if self.controller.connect():
                    return jsonify({'status': 'connected', 'port': port})
                else:
                    # Get the last error from the controller
                    error_msg = getattr(self.controller, 'last_error', 'Failed to connect to serial port')
                    if not error_msg:
                        error_msg = f'Failed to connect to {port}. Check if device is connected and port permissions.'
                    return jsonify({'error': error_msg}), 500
                    
            except Exception as e:
                self.logger.error(f"Connection failed: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/disconnect', methods=['POST'])
        def disconnect():
            """Disconnect from SA5X"""
            if self.controller:
                self.controller.disconnect()
                self.controller = None
                return jsonify({'status': 'disconnected'})
            return jsonify({'status': 'not_connected'})
        
        @self.app.route('/monitor/start', methods=['POST'])
        def start_monitoring():
            """Start continuous monitoring"""
            if not self.controller:
                return jsonify({'error': 'Controller not connected'}), 503
            
            data = request.get_json()
            interval = data.get('interval', 10)
            
            if self.monitoring_active:
                return jsonify({'error': 'Monitoring already active'}), 400
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(interval,),
                daemon=True
            )
            self.monitoring_thread.start()
            
            return jsonify({'status': 'monitoring_started', 'interval': interval})
        
        @self.app.route('/monitor/stop', methods=['POST'])
        def stop_monitoring():
            """Stop continuous monitoring"""
            self.monitoring_active = False
            return jsonify({'status': 'monitoring_stopped'})
        
        @self.app.route('/holdover/start', methods=['POST'])
        def start_holdover():
            """Start holdover mode"""
            if not self.controller:
                return jsonify({'error': 'Controller not connected'}), 503
            
            try:
                if self.controller.start_holdover():
                    return jsonify({'status': 'holdover_started'})
                else:
                    return jsonify({'error': 'Failed to start holdover'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/holdover/stop', methods=['POST'])
        def stop_holdover():
            """Stop holdover mode"""
            if not self.controller:
                return jsonify({'error': 'Controller not connected'}), 503
            
            try:
                if self.controller.stop_holdover():
                    return jsonify({'status': 'holdover_stopped'})
                else:
                    return jsonify({'error': 'Failed to stop holdover'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/test/holdover', methods=['POST'])
        def run_holdover_test():
            """Run holdover test"""
            if not self.controller:
                return jsonify({'error': 'Controller not connected'}), 503
            
            try:
                data = request.get_json()
                duration = data.get('duration', 3600)
                interval = data.get('interval', 10)
                output_file = data.get('output_file', f'holdover_test_{int(time.time())}.json')
                
                # Run test in background thread
                test_thread = threading.Thread(
                    target=self._run_holdover_test,
                    args=(duration, interval, output_file),
                    daemon=True
                )
                test_thread.start()
                
                return jsonify({
                    'status': 'test_started',
                    'duration': duration,
                    'interval': interval,
                    'output_file': output_file
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/test/results/<filename>')
        def get_test_results(filename):
            """Get test results from file"""
            try:
                filepath = Path('uploads') / filename
                if filepath.exists():
                    with open(filepath, 'r') as f:
                        results = json.load(f)
                    return jsonify(results)
                else:
                    return jsonify({'error': 'Results file not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/config', methods=['GET', 'POST'])
        def config():
            """Get or update configuration"""
            if request.method == 'GET':
                return jsonify(self.config.get_all())
            else:
                try:
                    data = request.get_json()
                    self.config.update(data)
                    return jsonify({'status': 'updated'})
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
        
        @self.app.route('/logs')
        def get_logs():
            """Get available log files"""
            try:
                log_dir = Path('uploads')
                if log_dir.exists():
                    log_files = [f.name for f in log_dir.glob('*.log')]
                    return jsonify({'logs': log_files})
                else:
                    return jsonify({'logs': []})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/upload', methods=['POST'])
        def upload_log():
            """Upload and parse log file"""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                filename = secure_filename(file.filename)
                filepath = Path('uploads') / filename
                filepath.parent.mkdir(exist_ok=True)
                file.save(str(filepath))
                
                # Parse log file
                parser = LogParser()
                results = parser.parse_holdover_log(str(filepath))
                
                # Сохраняем данные для использования в графиках
                self.uploaded_log_results = results
                self.uploaded_log_data = self._extract_log_data_for_charts(str(filepath))
                
                return jsonify({
                    'status': 'log_parsed',
                    'filename': filename,
                    'results': results
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/statistics')
        def get_statistics():
            """Get statistical analysis of current data"""
            try:
                if not self.current_data:
                    return jsonify({'error': 'No data available'}), 404
                
                # Calculate statistics from monitoring data
                stats = self._calculate_statistics()
                return jsonify(stats)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chart-data/<chart_type>')
        def get_chart_data(chart_type):
            """Get chart data for specific chart type"""
            try:
                # Проверяем, есть ли загруженные данные логов
                if self.uploaded_log_data and chart_type in ['frequency', 'temperature', 'electrical']:
                    return jsonify(self.uploaded_log_data[chart_type])
                
                if not self.current_data:
                    return jsonify({'error': 'No data available'}), 404
                
                data = self._get_chart_data(chart_type)
                return jsonify(data)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/allan-deviation/<data_type>')
        def get_allan_deviation(data_type):
            """Calculate and return Allan deviation for specified data type"""
            try:
                # Если есть загруженные данные логов, используем их
                if self.uploaded_log_results and data_type in ['frequency', 'temperature']:
                    allan_data = self._calculate_allan_deviation_from_log(data_type)
                    return jsonify(allan_data)
                
                if not self.current_data:
                    return jsonify({'error': 'No data available'}), 404
                
                allan_data = self._calculate_allan_deviation(data_type)
                return jsonify(allan_data)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/export-data')
        def export_data():
            """Export current monitoring data"""
            try:
                if not self.current_data:
                    return jsonify({'error': 'No data available'}), 404
                
                # Export data in various formats
                export_data = self._export_monitoring_data()
                return jsonify(export_data)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _setup_socket_events(self):
        """Setup SocketIO events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.logger.info('Client connected')
            emit('status', {'message': 'Connected to SA5X Monitor'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.logger.info('Client disconnected')
        
        @self.socketio.on('request_status')
        def handle_status_request():
            """Handle real-time status requests"""
            if self.controller and self.current_data:
                emit('status_update', self.current_data)
    
    def _monitoring_loop(self, interval):
        """Background monitoring loop"""
        self.logger.info(f"Starting monitoring loop with {interval}s interval")
        
        while self.monitoring_active:
            try:
                if self.controller:
                    data = self.controller.get_all_parameters()
                    data['timestamp'] = datetime.now().isoformat()
                    self.current_data = data
                    
                    # Emit to connected clients
                    self.socketio.emit('status_update', data)
                    
                    self.logger.debug(f"Monitoring update: {data}")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(interval)
        
        self.logger.info("Monitoring loop stopped")
    
    def _run_holdover_test(self, duration, interval, output_file):
        """Run holdover test in background"""
        try:
            self.logger.info(f"Starting holdover test: {duration}s, {interval}s interval")
            
            test = HoldoverTest(self.controller, self.config)
            results = test.run_test(duration, interval, output_file)
            
            # Emit test completion event
            self.socketio.emit('test_completed', {
                'output_file': output_file,
                'results': results
            })
            
            self.logger.info(f"Holdover test completed: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Holdover test failed: {e}")
            self.socketio.emit('test_error', {'error': str(e)})
    
    def _extract_log_data_for_charts(self, log_file):
        """Extract data from log file for chart display"""
        try:
            parser = LogParser()
            measurements = parser._parse_log_file(log_file)
            
            if not measurements:
                return None
            
            # Extract data arrays
            timestamps = [m['timestamp'] for m in measurements]
            freq_errors = [m['frequency_error'] for m in measurements]
            temperatures = [m['temperature'] for m in measurements]
            voltages = [m['voltage'] for m in measurements]
            currents = [m['current'] for m in measurements]
            
            # Format timestamps for display
            formatted_timestamps = [datetime.fromtimestamp(ts).strftime('%H:%M:%S') for ts in timestamps]
            
            return {
                'frequency': {
                    'labels': formatted_timestamps,
                    'datasets': [{
                        'label': 'Frequency Error (ppm)',
                        'data': freq_errors
                    }]
                },
                'temperature': {
                    'labels': formatted_timestamps,
                    'datasets': [{
                        'label': 'Temperature (°C)',
                        'data': temperatures
                    }]
                },
                'electrical': {
                    'labels': formatted_timestamps,
                    'datasets': [
                        {
                            'label': 'Voltage (V)',
                            'data': voltages
                        },
                        {
                            'label': 'Current (A)',
                            'data': currents
                        }
                    ]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract log data: {e}")
            return None
    
    def _calculate_allan_deviation_from_log(self, data_type):
        """Calculate Allan deviation from uploaded log data"""
        try:
            if not self.uploaded_log_results:
                return {'error': 'No log data available'}
            
            # Use the already parsed results
            results = self.uploaded_log_results
            
            if data_type == 'frequency':
                # Use the Allan deviation already calculated by the parser
                allan_deviations = results.get('allan_deviations', {})
                
                # Format data for chart
                allan_data = []
                for tau, dev in allan_deviations.items():
                    if dev > 0:  # Only include valid deviations
                        allan_data.append({
                            'tau': tau,
                            'allan_deviation': dev
                        })
                
                return {
                    'data_type': data_type,
                    'allan_data': allan_data,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'uploaded_log',
                    'total_measurements': results.get('measurement_count', 0),
                    'duration': results.get('duration', 0)
                }
            elif data_type == 'temperature':
                # For temperature, we would need to implement similar calculation
                # For now, return a simplified version
                return {
                    'data_type': data_type,
                    'allan_data': [],
                    'timestamp': datetime.now().isoformat(),
                    'source': 'uploaded_log',
                    'message': 'Temperature Allan deviation not yet implemented'
                }
            else:
                return {'error': 'Unknown data type'}
            
        except Exception as e:
            self.logger.error(f"Failed to calculate Allan deviation from log: {e}")
            return {'error': str(e)}
    
    def _calculate_statistics(self):
        """Calculate statistical analysis of monitoring data"""
        try:
            # This would typically use historical data from a database
            # For now, we'll use the current data point
            data = self.current_data
            
            stats = {
                'frequency_error': {
                    'current': data.get('frequency_error', 0),
                    'mean': data.get('frequency_error', 0),
                    'std_dev': 0,
                    'min': data.get('frequency_error', 0),
                    'max': data.get('frequency_error', 0)
                },
                'temperature': {
                    'current': data.get('temperature', 0),
                    'mean': data.get('temperature', 0),
                    'std_dev': 0,
                    'min': data.get('temperature', 0),
                    'max': data.get('temperature', 0)
                },
                'voltage': {
                    'current': data.get('voltage', 0),
                    'mean': data.get('voltage', 0),
                    'std_dev': 0,
                    'min': data.get('voltage', 0),
                    'max': data.get('voltage', 0)
                },
                'current': {
                    'current': data.get('current', 0),
                    'mean': data.get('current', 0),
                    'std_dev': 0,
                    'min': data.get('current', 0),
                    'max': data.get('current', 0)
                },
                'status': {
                    'lock_status': data.get('lock_status', False),
                    'holdover_status': data.get('holdover_status', False),
                    'overall_status': data.get('status', 'UNKNOWN')
                },
                'timestamp': data.get('timestamp', datetime.now().isoformat())
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to calculate statistics: {e}")
            return {}
    
    def _get_chart_data(self, chart_type):
        """Get chart data for specific chart type"""
        try:
            data = self.current_data
            
            if chart_type == 'frequency':
                return {
                    'labels': [data.get('timestamp', datetime.now().isoformat())],
                    'datasets': [{
                        'label': 'Frequency Error (ppm)',
                        'data': [data.get('frequency_error', 0)]
                    }]
                }
            elif chart_type == 'temperature':
                return {
                    'labels': [data.get('timestamp', datetime.now().isoformat())],
                    'datasets': [{
                        'label': 'Temperature (°C)',
                        'data': [data.get('temperature', 0)]
                    }]
                }
            elif chart_type == 'electrical':
                return {
                    'labels': [data.get('timestamp', datetime.now().isoformat())],
                    'datasets': [
                        {
                            'label': 'Voltage (V)',
                            'data': [data.get('voltage', 0)]
                        },
                        {
                            'label': 'Current (A)',
                            'data': [data.get('current', 0)]
                        }
                    ]
                }
            elif chart_type == 'status':
                return {
                    'labels': [data.get('timestamp', datetime.now().isoformat())],
                    'datasets': [
                        {
                            'label': 'Lock Status',
                            'data': [1 if data.get('lock_status', False) else 0]
                        },
                        {
                            'label': 'Holdover Status',
                            'data': [1 if data.get('holdover_status', False) else 0]
                        }
                    ]
                }
            else:
                return {'error': 'Unknown chart type'}
                
        except Exception as e:
            self.logger.error(f"Failed to get chart data: {e}")
            return {'error': str(e)}
    
    def _calculate_allan_deviation(self, data_type):
        """Calculate Allan deviation for specified data type"""
        try:
            # This is a simplified Allan deviation calculation
            # In a real implementation, you would need multiple data points over time
            data = self.current_data
            
            if data_type == 'frequency':
                value = data.get('frequency_error', 0)
            elif data_type == 'temperature':
                value = data.get('temperature', 0)
            else:
                return {'error': 'Unknown data type'}
            
            # Simplified Allan deviation calculation
            # In practice, you would need multiple data points over time
            allan_data = []
            for tau in range(1, 11):  # Sample tau values
                allan_dev = abs(value) / (tau ** 0.5)  # Simplified calculation
                allan_data.append({
                    'tau': tau,
                    'allan_deviation': allan_dev
                })
            
            return {
                'data_type': data_type,
                'allan_data': allan_data,
                'timestamp': data.get('timestamp', datetime.now().isoformat())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate Allan deviation: {e}")
            return {'error': str(e)}
    
    def _export_monitoring_data(self):
        """Export current monitoring data in various formats"""
        try:
            data = self.current_data
            
            export_data = {
                'json': data,
                'csv': self._convert_to_csv(data),
                'summary': {
                    'timestamp': data.get('timestamp', datetime.now().isoformat()),
                    'frequency_error': data.get('frequency_error', 0),
                    'temperature': data.get('temperature', 0),
                    'voltage': data.get('voltage', 0),
                    'current': data.get('current', 0),
                    'lock_status': data.get('lock_status', False),
                    'holdover_status': data.get('holdover_status', False),
                    'status': data.get('status', 'UNKNOWN')
                }
            }
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
            return {'error': str(e)}
    
    def _convert_to_csv(self, data):
        """Convert data to CSV format"""
        try:
            csv_lines = []
            csv_lines.append('timestamp,frequency_error,temperature,voltage,current,lock_status,holdover_status,status')
            
            timestamp = data.get('timestamp', datetime.now().isoformat())
            freq_error = data.get('frequency_error', 0)
            temp = data.get('temperature', 0)
            voltage = data.get('voltage', 0)
            current = data.get('current', 0)
            lock_status = 1 if data.get('lock_status', False) else 0
            holdover_status = 1 if data.get('holdover_status', False) else 0
            status = data.get('status', 'UNKNOWN')
            
            csv_lines.append(f'{timestamp},{freq_error},{temp},{voltage},{current},{lock_status},{holdover_status},{status}')
            
            return '\n'.join(csv_lines)
            
        except Exception as e:
            self.logger.error(f"Failed to convert to CSV: {e}")
            return ''
    
    def run(self, host='localhost', port=8080, debug=False):
        """Run the web application"""
        self.logger.info(f"Starting SA5X Web Monitor on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    monitor = SA5XWebMonitor()
    monitor.run()