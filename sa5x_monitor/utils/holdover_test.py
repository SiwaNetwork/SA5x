"""
Holdover Test Module for SA5X
Based on self_holdover.sh and parse_holdover_log.py
"""

import time
import logging
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class HoldoverTest:
    """Holdover test implementation for SA5X"""
    
    def __init__(self, controller, config):
        self.controller = controller
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Test parameters
        self.min_duration = 300  # 5 minutes minimum
        self.max_duration = 86400  # 24 hours maximum
        self.min_interval = 1  # 1 second minimum
        self.max_interval = 60  # 60 seconds maximum
        
    def run_test(self, duration: int, interval: int, output_file: str) -> Dict[str, Any]:
        """Run holdover test"""
        
        # Validate parameters
        if duration < self.min_duration:
            raise ValueError(f"Duration must be at least {self.min_duration} seconds")
        if duration > self.max_duration:
            raise ValueError(f"Duration must be at most {self.max_duration} seconds")
        if interval < self.min_interval:
            raise ValueError(f"Interval must be at least {self.min_interval} second")
        if interval > self.max_interval:
            raise ValueError(f"Interval must be at most {self.max_interval} seconds")
        
        self.logger.info(f"Starting holdover test: duration={duration}s, interval={interval}s")
        
        # Initialize test data
        test_data = {
            'start_time': datetime.now().isoformat(),
            'duration': duration,
            'interval': interval,
            'measurements': []
        }
        
        # Start holdover mode
        if not self.controller.start_holdover():
            raise RuntimeError("Failed to start holdover mode")
        
        self.logger.info("Holdover mode started")
        
        try:
            # Run measurements
            start_time = time.time()
            measurement_count = 0
            
            while time.time() - start_time < duration:
                measurement_time = time.time()
                
                # Get measurements
                freq_error = self.controller.get_frequency_error()
                temperature = self.controller.get_temperature()
                voltage = self.controller.get_voltage()
                current = self.controller.get_current()
                status = self.controller.get_status()
                
                # Store measurement
                measurement = {
                    'timestamp': measurement_time,
                    'elapsed_time': measurement_time - start_time,
                    'frequency_error': freq_error,
                    'temperature': temperature,
                    'voltage': voltage,
                    'current': current,
                    'status': status
                }
                
                test_data['measurements'].append(measurement)
                measurement_count += 1
                
                self.logger.debug(f"Measurement {measurement_count}: "
                                f"freq_error={freq_error:.2e}, "
                                f"temp={temperature:.2f}°C, "
                                f"status={status}")
                
                # Wait for next measurement
                time.sleep(interval)
            
            # Stop holdover mode
            self.controller.stop_holdover()
            self.logger.info("Holdover mode stopped")
            
            # Calculate results
            results = self._calculate_results(test_data)
            test_data['results'] = results
            
            # Save results
            self._save_results(test_data, output_file)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Holdover test failed: {e}")
            self.controller.stop_holdover()
            raise
    
    def _calculate_results(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate test results from measurement data"""
        
        measurements = test_data['measurements']
        if len(measurements) < 2:
            raise ValueError("Insufficient measurements for analysis")
        
        # Extract data arrays
        elapsed_times = np.array([m['elapsed_time'] for m in measurements])
        freq_errors = np.array([m['frequency_error'] for m in measurements])
        temperatures = np.array([m['temperature'] for m in measurements])
        
        # Calculate frequency stability metrics
        freq_stability = np.std(freq_errors)
        freq_drift = np.polyfit(elapsed_times, freq_errors, 1)[0]  # Linear drift rate
        
        # Calculate Allan Deviation (simplified)
        tau_values = [1, 10, 100, 1000]  # Tau values in seconds
        allan_deviations = []
        
        for tau in tau_values:
            if tau < len(measurements) // 2:
                # Calculate Allan deviation for this tau
                m = len(measurements) // tau
                if m > 1:
                    freq_diff = np.diff(freq_errors[:m*tau:tau])
                    allan_dev = np.sqrt(np.mean(freq_diff**2) / 2)
                    allan_deviations.append(allan_dev)
                else:
                    allan_deviations.append(0.0)
            else:
                allan_deviations.append(0.0)
        
        # Calculate temperature stability
        temp_stability = np.std(temperatures)
        temp_drift = np.polyfit(elapsed_times, temperatures, 1)[0]
        
        # Calculate Allan Deviation at tau=1s (most common metric)
        allan_deviation_1s = allan_deviations[0] if allan_deviations else 0.0
        
        results = {
            'test_duration': elapsed_times[-1],
            'measurement_count': len(measurements),
            'freq_stability': freq_stability,
            'freq_drift_rate': freq_drift,
            'allan_deviation_1s': allan_deviation_1s,
            'allan_deviations': dict(zip(tau_values, allan_deviations)),
            'temp_stability': temp_stability,
            'temp_drift_rate': temp_drift,
            'freq_error_min': np.min(freq_errors),
            'freq_error_max': np.max(freq_errors),
            'freq_error_mean': np.mean(freq_errors),
            'temp_min': np.min(temperatures),
            'temp_max': np.max(temperatures),
            'temp_mean': np.mean(temperatures)
        }
        
        return results
    
    def _save_results(self, test_data: Dict[str, Any], output_file: str):
        """Save test results to file"""
        
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results as JSON
        with open(output_file, 'w') as f:
            json.dump(test_data, f, indent=2, default=str)
        
        # Save summary as text file
        summary_file = output_file.replace('.json', '_summary.txt')
        results = test_data['results']
        
        with open(summary_file, 'w') as f:
            f.write("SA5X Holdover Test Results\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Test Duration: {results['test_duration']:.2f} seconds\n")
            f.write(f"Measurement Count: {results['measurement_count']}\n\n")
            
            f.write("Frequency Stability:\n")
            f.write(f"  Stability (std): {results['freq_stability']:.2e}\n")
            f.write(f"  Drift Rate: {results['freq_drift_rate']:.2e}/s\n")
            f.write(f"  Allan Deviation (1s): {results['allan_deviation_1s']:.2e}\n")
            f.write(f"  Min Error: {results['freq_error_min']:.2e}\n")
            f.write(f"  Max Error: {results['freq_error_max']:.2e}\n")
            f.write(f"  Mean Error: {results['freq_error_mean']:.2e}\n\n")
            
            f.write("Temperature Stability:\n")
            f.write(f"  Stability (std): {results['temp_stability']:.3f}°C\n")
            f.write(f"  Drift Rate: {results['temp_drift_rate']:.3f}°C/s\n")
            f.write(f"  Min Temp: {results['temp_min']:.2f}°C\n")
            f.write(f"  Max Temp: {results['temp_max']:.2f}°C\n")
            f.write(f"  Mean Temp: {results['temp_mean']:.2f}°C\n\n")
            
            f.write("Allan Deviations:\n")
            for tau, dev in results['allan_deviations'].items():
                f.write(f"  τ={tau}s: {dev:.2e}\n")
        
        self.logger.info(f"Results saved to {output_file} and {summary_file}")
    
    def analyze_existing_log(self, log_file: str) -> Dict[str, Any]:
        """Analyze existing holdover log file"""
        
        if not Path(log_file).exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")
        
        # Parse log file
        measurements = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    # Parse log line format: timestamp,freq_error,temperature,voltage,current,status
                    parts = line.strip().split(',')
                    if len(parts) >= 6:
                        measurement = {
                            'timestamp': float(parts[0]),
                            'elapsed_time': float(parts[0]),
                            'frequency_error': float(parts[1]),
                            'temperature': float(parts[2]),
                            'voltage': float(parts[3]),
                            'current': float(parts[4]),
                            'status': parts[5]
                        }
                        measurements.append(measurement)
                except (ValueError, IndexError):
                    continue
        
        if not measurements:
            raise ValueError("No valid measurements found in log file")
        
        # Create test data structure
        test_data = {
            'start_time': datetime.fromtimestamp(measurements[0]['timestamp']).isoformat(),
            'measurements': measurements
        }
        
        # Calculate results
        results = self._calculate_results(test_data)
        
        return results