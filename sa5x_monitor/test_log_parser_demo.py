#!/usr/bin/env python3
"""
Test script for LogParser with demo files
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from utils.log_parser import LogParser

def test_log_parser():
    """Test LogParser with demo files"""
    
    parser = LogParser()
    
    # Test files
    test_files = [
        'uploads/demo_holdover_test.log',
        'uploads/demo_holdover_test_alt.log', 
        'uploads/demo_holdover_test.csv'
    ]
    
    print("Testing LogParser with demo files...")
    print("=" * 50)
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"❌ File not found: {test_file}")
            continue
            
        print(f"\n📁 Testing file: {test_file}")
        print("-" * 30)
        
        try:
            # Parse the log file
            results = parser.parse_holdover_log(test_file)
            
            # Display results
            print(f"✅ Successfully parsed {test_file}")
            print(f"   Duration: {results['duration']:.2f} seconds")
            print(f"   Measurements: {results['measurement_count']}")
            print(f"   Frequency stability: {results['freq_stability']:.2e}")
            print(f"   Allan deviation (1s): {results['allan_deviation']:.2e}")
            print(f"   Temperature stability: {results['temp_stability']:.3f}°C")
            print(f"   Primary status: {results['primary_status']}")
            
        except Exception as e:
            print(f"❌ Failed to parse {test_file}: {e}")
    
    print("\n" + "=" * 50)
    print("Demo files created successfully!")
    print("You can now test the Log Analysis feature in the web interface.")
    print("Upload any of these files:")
    for test_file in test_files:
        print(f"   - {test_file}")

if __name__ == "__main__":
    test_log_parser()