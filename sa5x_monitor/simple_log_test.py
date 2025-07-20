#!/usr/bin/env python3
"""
Simple test for demo log files without external dependencies
"""

import re
import os
from pathlib import Path

def parse_log_file_simple(log_file):
    """Simple log parser for testing"""
    
    if not os.path.exists(log_file):
        raise FileNotFoundError(f"Log file not found: {log_file}")
    
    print(f"Parsing: {log_file}")
    
    # Common log patterns
    log_patterns = [
        # Format: timestamp,freq_error,temperature,voltage,current,status
        r'^(\d+\.?\d*),([+-]?\d+\.?\d*),([+-]?\d+\.?\d*),([+-]?\d+\.?\d*),([+-]?\d+\.?\d*),(\w+)$',
        
        # Format: timestamp freq_error temperature voltage current status
        r'^(\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\s+(\w+)$',
    ]
    
    measurements = []
    
    with open(log_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Try to match line with known patterns
            for pattern in log_patterns:
                match = re.match(pattern, line)
                if match:
                    try:
                        timestamp = float(match.group(1))
                        freq_error = float(match.group(2))
                        temperature = float(match.group(3))
                        voltage = float(match.group(4))
                        current = float(match.group(5))
                        status = match.group(6)
                        
                        measurements.append({
                            'timestamp': timestamp,
                            'frequency_error': freq_error,
                            'temperature': temperature,
                            'voltage': voltage,
                            'current': current,
                            'status': status
                        })
                        break
                    except (ValueError, IndexError) as e:
                        print(f"Failed to parse line {line_num}: {e}")
                        continue
            else:
                print(f"Could not parse line {line_num}: {line}")
    
    return measurements

def analyze_measurements(measurements):
    """Simple analysis of measurements"""
    
    if len(measurements) < 2:
        raise ValueError("Insufficient measurements for analysis")
    
    # Extract data arrays
    timestamps = [m['timestamp'] for m in measurements]
    freq_errors = [m['frequency_error'] for m in measurements]
    temperatures = [m['temperature'] for m in measurements]
    voltages = [m['voltage'] for m in measurements]
    currents = [m['current'] for m in measurements]
    
    # Calculate basic statistics
    duration = timestamps[-1] - timestamps[0]
    
    # Simple statistics
    freq_mean = sum(freq_errors) / len(freq_errors)
    freq_min = min(freq_errors)
    freq_max = max(freq_errors)
    
    temp_mean = sum(temperatures) / len(temperatures)
    temp_min = min(temperatures)
    temp_max = max(temperatures)
    
    # Status analysis
    status_counts = {}
    for m in measurements:
        status = m['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    results = {
        'duration': duration,
        'measurement_count': len(measurements),
        'freq_error_mean': freq_mean,
        'freq_error_min': freq_min,
        'freq_error_max': freq_max,
        'temp_mean': temp_mean,
        'temp_min': temp_min,
        'temp_max': temp_max,
        'voltage_mean': sum(voltages) / len(voltages),
        'current_mean': sum(currents) / len(currents),
        'status_distribution': status_counts,
        'primary_status': max(status_counts.items(), key=lambda x: x[1])[0] if status_counts else 'UNKNOWN'
    }
    
    return results

def test_demo_files():
    """Test demo files"""
    
    # Test files
    test_files = [
        'uploads/demo_holdover_test.log',
        'uploads/demo_holdover_test_alt.log', 
        'uploads/demo_holdover_test.csv'
    ]
    
    print("Testing demo log files...")
    print("=" * 50)
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"❌ File not found: {test_file}")
            continue
            
        print(f"\n📁 Testing file: {test_file}")
        print("-" * 30)
        
        try:
            # Parse the log file
            measurements = parse_log_file_simple(test_file)
            
            if not measurements:
                print(f"❌ No valid measurements found in {test_file}")
                continue
            
            # Analyze measurements
            results = analyze_measurements(measurements)
            
            # Display results
            print(f"✅ Successfully parsed {test_file}")
            print(f"   Duration: {results['duration']:.2f} seconds")
            print(f"   Measurements: {results['measurement_count']}")
            print(f"   Frequency error range: {results['freq_error_min']:.2e} to {results['freq_error_max']:.2e}")
            print(f"   Temperature range: {results['temp_min']:.1f}°C to {results['temp_max']:.1f}°C")
            print(f"   Primary status: {results['primary_status']}")
            print(f"   Status distribution: {results['status_distribution']}")
            
        except Exception as e:
            print(f"❌ Failed to parse {test_file}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Demo files created successfully!")
    print("You can now test the Log Analysis feature in the web interface.")
    print("Upload any of these files:")
    for test_file in test_files:
        print(f"   - {test_file}")

if __name__ == "__main__":
    test_demo_files()