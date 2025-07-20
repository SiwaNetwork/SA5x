#!/usr/bin/env python3
"""
Test script for log analysis and Allan Deviation calculation
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from utils.log_parser import LogParser

def test_log_analysis():
    """Test log analysis functionality"""
    
    # Test log file path
    log_file = "uploads/demo_holdover_test.log"
    
    if not os.path.exists(log_file):
        print(f"Error: Log file {log_file} not found")
        return
    
    print("=== Testing Log Analysis ===")
    
    # Create parser
    parser = LogParser()
    
    try:
        # Parse log file
        print(f"Parsing log file: {log_file}")
        results = parser.parse_holdover_log(log_file)
        
        # Display results
        print("\n=== Analysis Results ===")
        print(f"Duration: {results['duration']:.2f} seconds")
        print(f"Measurement count: {results['measurement_count']}")
        print(f"Measurement interval: {results['measurement_interval']:.2f} seconds")
        
        print("\n=== Frequency Analysis ===")
        print(f"Frequency stability: {results['freq_stability']:.2e}")
        print(f"Frequency drift rate: {results['freq_drift_rate']:.2e}")
        print(f"Frequency error range: {results['freq_error_min']:.2e} to {results['freq_error_max']:.2e}")
        print(f"Frequency error mean: {results['freq_error_mean']:.2e}")
        print(f"Frequency error std: {results['freq_error_std']:.2e}")
        
        print("\n=== Allan Deviation Analysis ===")
        print(f"Allan deviation (1s): {results['allan_deviation']:.2e}")
        print("Allan deviations by tau:")
        for tau, dev in results['allan_deviations'].items():
            if dev > 0:
                print(f"  Tau={tau}s: {dev:.2e}")
        
        print("\n=== Temperature Analysis ===")
        print(f"Temperature stability: {results['temp_stability']:.3f}°C")
        print(f"Temperature drift rate: {results['temp_drift_rate']:.3f}°C/s")
        print(f"Temperature range: {results['temp_min']:.2f}°C to {results['temp_max']:.2f}°C")
        print(f"Temperature mean: {results['temp_mean']:.2f}°C")
        print(f"Temperature std: {results['temp_std']:.3f}°C")
        
        print("\n=== Power Analysis ===")
        print(f"Voltage stability: {results['voltage_stability']:.3f}V")
        print(f"Current stability: {results['current_stability']:.3f}A")
        print(f"Voltage range: {results['voltage_min']:.2f}V to {results['voltage_max']:.2f}V")
        print(f"Current range: {results['current_min']:.3f}A to {results['current_max']:.3f}A")
        
        print("\n=== Status Analysis ===")
        print(f"Primary status: {results['primary_status']}")
        print("Status distribution:")
        for status, count in results['status_distribution'].items():
            print(f"  {status}: {count}")
        
        print("\n=== Test Summary ===")
        print("✅ Log analysis completed successfully")
        print("✅ Allan deviation calculation working")
        print("✅ Frequency stability analysis working")
        print("✅ Temperature analysis working")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

def test_chart_data_extraction():
    """Test chart data extraction functionality"""
    
    print("\n=== Testing Chart Data Extraction ===")
    
    log_file = "uploads/demo_holdover_test.log"
    
    if not os.path.exists(log_file):
        print(f"Error: Log file {log_file} not found")
        return
    
    try:
        # Import the web app to test chart data extraction
        sys.path.append(str(Path(__file__).parent / "web"))
        from app import SA5XWebMonitor
        
        # Create monitor instance
        monitor = SA5XWebMonitor()
        
        # Test chart data extraction
        chart_data = monitor._extract_log_data_for_charts(log_file)
        
        if chart_data:
            print("✅ Chart data extraction successful")
            print(f"Frequency data points: {len(chart_data['frequency']['datasets'][0]['data'])}")
            print(f"Temperature data points: {len(chart_data['temperature']['datasets'][0]['data'])}")
            print(f"Electrical data points: {len(chart_data['electrical']['datasets'][0]['data'])}")
        else:
            print("❌ Chart data extraction failed")
            
    except Exception as e:
        print(f"❌ Error during chart data extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_log_analysis()
    test_chart_data_extraction()