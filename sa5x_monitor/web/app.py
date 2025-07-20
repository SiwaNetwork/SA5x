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
                port = data.get('port', '/dev/ttyUSB0')
                baudrate = data.get('baudrate', 115200)
                timeout = data.get('timeout', 1.0)
                
                self.controller = SA5XController(port, baudrate, timeout)
                if self.controller.connect():
                    return jsonify({'status': 'connected', 'port': port})
                else:
                    return jsonify({'error': 'Failed to connect'}), 500
                    
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
            """Get test results"""
            try:
                results_file = Path('results') / filename
                if results_file.exists():
                    with open(results_file, 'r') as f:
                        data = json.load(f)
                    return jsonify(data)
                else:
                    return jsonify({'error': 'Results file not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/config', methods=['GET', 'POST'])
        def config():
            """Configuration management"""
            if request.method == 'GET':
                return jsonify(self.config.get_config_summary())
            else:
                try:
                    data = request.get_json()
                    for key, value in data.items():
                        self.config.set(key, value)
                    return jsonify({'status': 'config_updated'})
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
        
        @self.app.route('/logs')
        def get_logs():
            """Get recent logs"""
            try:
                log_file = self.config.get('logging.log_file', 'sa5x_monitor.log')
                if Path(log_file).exists():
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                    return jsonify({'logs': lines[-100:]})  # Last 100 lines
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
                
                return jsonify({
                    'status': 'log_parsed',
                    'filename': filename,
                    'results': results
                })
                
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
    
    def run(self, host='localhost', port=8080, debug=False):
        """Run the web application"""
        self.logger.info(f"Starting SA5X Web Monitor on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    monitor = SA5XWebMonitor()
    monitor.run()