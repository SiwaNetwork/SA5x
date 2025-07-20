"""
Log Parser for SA5X Holdover Tests
Based on parse_holdover_log.py
"""

import re
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class LogParser:
    """Parser for SA5X holdover test logs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Common log formats
        self.log_patterns = [
            # Format: timestamp,freq_error,temperature,voltage,current,status
            r'^(\d+\.?\d*),([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?),([+-]?\d+\.?\d*),([+-]?\d+\.?\d*),([+-]?\d+\.?\d*),(\w+)$',
            
            # Format: timestamp freq_error temperature voltage current status
            r'^(\d+\.?\d*)\s+([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)\s+([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+(\w+)$',
            
            # Format: [timestamp] freq_error temp voltage current status
            r'^\[(\d+\.?\d*)\]\s+([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)\s+([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+(\w+)$',
            
            # Format: timestamp: freq_error, temp, voltage, current, status
            r'^(\d+\.?\d*):\s*([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?),\s*([+-]?\d+\.?\d*),\s*([+-]?\d+\.?\d*),\s*([+-]?\d+\.?\d*),\s*(\w+)$'
        ]
    
    def parse_holdover_log(self, log_file: str) -> Dict[str, Any]:
        """Parse holdover log file and return analysis results"""
        
        if not Path(log_file).exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")
        
        self.logger.info(f"Parsing holdover log: {log_file}")
        
        # Parse log file
        measurements = self._parse_log_file(log_file)
        
        if not measurements:
            raise ValueError("No valid measurements found in log file")
        
        # Calculate analysis results
        results = self._analyze_measurements(measurements)
        
        return results
    
    def _parse_log_file(self, log_file: str) -> List[Dict[str, Any]]:
        """Parse log file and extract measurements"""
        
        measurements = []
        
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Try to match line with known patterns
                measurement = self._parse_line(line)
                if measurement:
                    measurement['line_number'] = line_num
                    measurements.append(measurement)
                else:
                    self.logger.warning(f"Could not parse line {line_num}: {line}")
        
        return measurements
    
    def _parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line"""
        
        for pattern in self.log_patterns:
            match = re.match(pattern, line)
            if match:
                try:
                    timestamp = float(match.group(1))
                    freq_error = float(match.group(2))
                    temperature = float(match.group(3))
                    voltage = float(match.group(4))
                    current = float(match.group(5))
                    status = match.group(6)
                    
                    return {
                        'timestamp': timestamp,
                        'elapsed_time': timestamp,
                        'frequency_error': freq_error,
                        'temperature': temperature,
                        'voltage': voltage,
                        'current': current,
                        'status': status
                    }
                except (ValueError, IndexError) as e:
                    self.logger.debug(f"Failed to parse matched line: {e}")
                    continue
        
        return None
    
    def _analyze_measurements(self, measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze measurement data and calculate statistics"""
        
        if len(measurements) < 2:
            raise ValueError("Insufficient measurements for analysis")
        
        # Extract data arrays
        elapsed_times = np.array([m['elapsed_time'] for m in measurements])
        freq_errors = np.array([m['frequency_error'] for m in measurements])
        temperatures = np.array([m['temperature'] for m in measurements])
        voltages = np.array([m['voltage'] for m in measurements])
        currents = np.array([m['current'] for m in measurements])
        
        # Calculate basic statistics
        duration = elapsed_times[-1] - elapsed_times[0]
        
        # Frequency stability analysis
        freq_stability = np.std(freq_errors)
        freq_drift = np.polyfit(elapsed_times, freq_errors, 1)[0]
        
        # Calculate Allan Deviation
        allan_deviations = self._calculate_allan_deviation(freq_errors, elapsed_times)
        
        # Temperature stability analysis
        temp_stability = np.std(temperatures)
        temp_drift = np.polyfit(elapsed_times, temperatures, 1)[0]
        
        # Voltage and current analysis
        voltage_stability = np.std(voltages)
        current_stability = np.std(currents)
        
        # Status analysis
        status_counts = {}
        for m in measurements:
            status = m['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        results = {
            'duration': duration,
            'measurement_count': len(measurements),
            'measurement_interval': duration / (len(measurements) - 1) if len(measurements) > 1 else 0,
            
            # Frequency analysis
            'freq_stability': freq_stability,
            'freq_drift_rate': freq_drift,
            'freq_error_min': np.min(freq_errors),
            'freq_error_max': np.max(freq_errors),
            'freq_error_mean': np.mean(freq_errors),
            'freq_error_std': np.std(freq_errors),
            
            # Allan deviation analysis
            'allan_deviation': allan_deviations.get(1, 0.0),  # 1-second Allan deviation
            'allan_deviations': allan_deviations,
            
            # Temperature analysis
            'temp_stability': temp_stability,
            'temp_drift_rate': temp_drift,
            'temp_min': np.min(temperatures),
            'temp_max': np.max(temperatures),
            'temp_mean': np.mean(temperatures),
            'temp_std': np.std(temperatures),
            
            # Power analysis
            'voltage_stability': voltage_stability,
            'current_stability': current_stability,
            'voltage_min': np.min(voltages),
            'voltage_max': np.max(voltages),
            'voltage_mean': np.mean(voltages),
            'current_min': np.min(currents),
            'current_max': np.max(currents),
            'current_mean': np.mean(currents),
            
            # Status analysis
            'status_distribution': status_counts,
            'primary_status': max(status_counts.items(), key=lambda x: x[1])[0] if status_counts else 'UNKNOWN'
        }
        
        return results
    
    def _calculate_allan_deviation(self, freq_errors: np.ndarray, elapsed_times: np.ndarray) -> Dict[int, float]:
        """Calculate Allan deviation for different tau values"""
        
        tau_values = [1, 10, 100, 1000]  # Tau values in seconds
        allan_deviations = {}
        
        for tau in tau_values:
            # Find measurements at tau intervals
            tau_indices = []
            current_time = elapsed_times[0]
            
            for i, time_val in enumerate(elapsed_times):
                if time_val >= current_time:
                    tau_indices.append(i)
                    current_time += tau
            
            if len(tau_indices) < 2:
                allan_deviations[tau] = 0.0
                continue
            
            # Calculate frequency differences at tau intervals
            freq_at_tau = freq_errors[tau_indices]
            freq_diff = np.diff(freq_at_tau)
            
            # Calculate Allan deviation
            if len(freq_diff) > 0:
                allan_dev = np.sqrt(np.mean(freq_diff**2) / 2)
                allan_deviations[tau] = allan_dev
            else:
                allan_deviations[tau] = 0.0
        
        return allan_deviations
    
    def parse_multiple_logs(self, log_files: List[str]) -> Dict[str, Any]:
        """Parse multiple log files and compare results"""
        
        all_results = {}
        
        for log_file in log_files:
            try:
                results = self.parse_holdover_log(log_file)
                all_results[log_file] = results
            except Exception as e:
                self.logger.error(f"Failed to parse {log_file}: {e}")
                all_results[log_file] = {'error': str(e)}
        
        return all_results
    
    def generate_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """Generate a formatted report from analysis results"""
        
        report = []
        report.append("SA5X Holdover Test Analysis Report")
        report.append("=" * 50)
        report.append("")
        
        # Test overview
        report.append("Test Overview:")
        report.append(f"  Duration: {results['duration']:.2f} seconds")
        report.append(f"  Measurement Count: {results['measurement_count']}")
        report.append(f"  Average Interval: {results['measurement_interval']:.2f} seconds")
        report.append("")
        
        # Frequency stability
        report.append("Frequency Stability Analysis:")
        report.append(f"  Stability (std): {results['freq_stability']:.2e}")
        report.append(f"  Drift Rate: {results['freq_drift_rate']:.2e}/s")
        report.append(f"  Allan Deviation (1s): {results['allan_deviation']:.2e}")
        report.append(f"  Min Error: {results['freq_error_min']:.2e}")
        report.append(f"  Max Error: {results['freq_error_max']:.2e}")
        report.append(f"  Mean Error: {results['freq_error_mean']:.2e}")
        report.append("")
        
        # Allan deviations
        report.append("Allan Deviations:")
        for tau, dev in results['allan_deviations'].items():
            report.append(f"  τ={tau}s: {dev:.2e}")
        report.append("")
        
        # Temperature stability
        report.append("Temperature Stability:")
        report.append(f"  Stability (std): {results['temp_stability']:.3f}°C")
        report.append(f"  Drift Rate: {results['temp_drift_rate']:.3f}°C/s")
        report.append(f"  Min Temp: {results['temp_min']:.2f}°C")
        report.append(f"  Max Temp: {results['temp_max']:.2f}°C")
        report.append(f"  Mean Temp: {results['temp_mean']:.2f}°C")
        report.append("")
        
        # Power analysis
        report.append("Power Analysis:")
        report.append(f"  Voltage Stability: {results['voltage_stability']:.3f}V")
        report.append(f"  Current Stability: {results['current_stability']:.3f}A")
        report.append(f"  Voltage Range: {results['voltage_min']:.2f}V - {results['voltage_max']:.2f}V")
        report.append(f"  Current Range: {results['current_min']:.3f}A - {results['current_max']:.3f}A")
        report.append("")
        
        # Status analysis
        report.append("Status Analysis:")
        for status, count in results['status_distribution'].items():
            percentage = (count / results['measurement_count']) * 100
            report.append(f"  {status}: {count} ({percentage:.1f}%)")
        report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            self.logger.info(f"Report saved to {output_file}")
        
        return report_text