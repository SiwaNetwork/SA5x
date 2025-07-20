#!/usr/bin/env python3
"""
Test script for SA5X Monitor graphs
Demonstrates graph functionality with simulated data
"""

import time
import random
import math
from datetime import datetime
import json

class SA5XGraphTester:
    """Test class for demonstrating graph functionality"""
    
    def __init__(self):
        self.time_counter = 0
        self.base_frequency_error = 0.0
        self.base_temperature = 25.0
        self.base_voltage = 12.0
        self.base_current = 0.5
        
    def generate_simulated_data(self):
        """Generate realistic simulated SA5X data"""
        self.time_counter += 1
        
        # Simulate frequency error with drift and noise
        drift = 0.0001 * self.time_counter  # Gradual drift
        noise = random.gauss(0, 0.00001)    # Random noise
        self.base_frequency_error += drift + noise
        
        # Simulate temperature with thermal cycling
        thermal_cycle = 2 * math.sin(self.time_counter * 0.1)  # Thermal cycling
        temp_noise = random.gauss(0, 0.1)   # Temperature noise
        self.base_temperature = 25.0 + thermal_cycle + temp_noise
        
        # Simulate voltage with small variations
        voltage_variation = random.gauss(0, 0.05)
        self.base_voltage = 12.0 + voltage_variation
        
        # Simulate current with load variations
        current_variation = random.gauss(0, 0.02)
        self.base_current = 0.5 + current_variation
        
        # Simulate lock status (mostly locked, occasional losses)
        lock_status = random.random() > 0.02  # 98% locked
        
        # Simulate holdover status
        holdover_status = random.random() > 0.95  # 5% in holdover
        
        return {
            'timestamp': datetime.now().isoformat(),
            'frequency_error': self.base_frequency_error,
            'temperature': self.base_temperature,
            'voltage': self.base_voltage,
            'current': self.base_current,
            'lock_status': lock_status,
            'holdover_status': holdover_status,
            'status': 'LOCKED' if lock_status else 'NOT_LOCKED'
        }
    
    def calculate_allan_deviation(self, data_points, tau_values):
        """Calculate Allan deviation for given data points"""
        allan_data = []
        
        for tau in tau_values:
            if tau >= len(data_points) // 2:
                continue
                
            sum_squares = 0
            count = 0
            
            for i in range(len(data_points) - 2 * tau):
                diff = data_points[i + 2 * tau] - 2 * data_points[i + tau] + data_points[i]
                sum_squares += diff * diff
                count += 1
            
            if count > 0:
                allan_dev = math.sqrt(sum_squares / (2 * count * tau * tau))
                allan_data.append({
                    'tau': tau,
                    'allan_deviation': allan_dev
                })
        
        return allan_data
    
    def run_graph_demo(self, duration=60, interval=1):
        """Run a demonstration of graph functionality"""
        print(f"Starting SA5X Graph Demo for {duration} seconds...")
        print("=" * 50)
        
        data_history = {
            'timestamps': [],
            'frequency_error': [],
            'temperature': [],
            'voltage': [],
            'current': []
        }
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Generate data
            data = self.generate_simulated_data()
            
            # Store in history
            data_history['timestamps'].append(data['timestamp'])
            data_history['frequency_error'].append(data['frequency_error'])
            data_history['temperature'].append(data['temperature'])
            data_history['voltage'].append(data['voltage'])
            data_history['current'].append(data['current'])
            
            # Keep only last 100 points
            if len(data_history['timestamps']) > 100:
                data_history['timestamps'].pop(0)
                data_history['frequency_error'].pop(0)
                data_history['temperature'].pop(0)
                data_history['voltage'].pop(0)
                data_history['current'].pop(0)
            
            # Display current status
            print(f"\rTime: {data['timestamp']} | "
                  f"Freq Error: {data['frequency_error']:.6f} ppm | "
                  f"Temp: {data['temperature']:.2f}°C | "
                  f"Voltage: {data['voltage']:.2f}V | "
                  f"Current: {data['current']:.3f}A | "
                  f"Lock: {'✓' if data['lock_status'] else '✗'}", end='')
            
            time.sleep(interval)
        
        print("\n\nDemo completed!")
        print("=" * 50)
        
        # Calculate and display statistics
        self.display_statistics(data_history)
        
        # Calculate Allan deviation
        self.display_allan_analysis(data_history)
        
        # Save data for web interface testing
        self.save_demo_data(data_history)
    
    def display_statistics(self, data_history):
        """Display statistical analysis of collected data"""
        print("\n📊 STATISTICAL ANALYSIS")
        print("-" * 30)
        
        freq_data = data_history['frequency_error']
        temp_data = data_history['temperature']
        voltage_data = data_history['voltage']
        current_data = data_history['current']
        
        # Frequency statistics
        freq_mean = sum(freq_data) / len(freq_data)
        freq_std = math.sqrt(sum((x - freq_mean) ** 2 for x in freq_data) / len(freq_data))
        freq_min, freq_max = min(freq_data), max(freq_data)
        
        print(f"Frequency Error:")
        print(f"  Mean: {freq_mean:.6f} ppm")
        print(f"  Std Dev: {freq_std:.6f} ppm")
        print(f"  Range: {freq_min:.6f} to {freq_max:.6f} ppm")
        
        # Temperature statistics
        temp_mean = sum(temp_data) / len(temp_data)
        temp_std = math.sqrt(sum((x - temp_mean) ** 2 for x in temp_data) / len(temp_data))
        temp_min, temp_max = min(temp_data), max(temp_data)
        
        print(f"\nTemperature:")
        print(f"  Mean: {temp_mean:.2f}°C")
        print(f"  Std Dev: {temp_std:.2f}°C")
        print(f"  Range: {temp_min:.2f} to {temp_max:.2f}°C")
        
        # Voltage statistics
        voltage_mean = sum(voltage_data) / len(voltage_data)
        voltage_std = math.sqrt(sum((x - voltage_mean) ** 2 for x in voltage_data) / len(voltage_data))
        
        print(f"\nVoltage:")
        print(f"  Mean: {voltage_mean:.2f}V")
        print(f"  Std Dev: {voltage_std:.2f}V")
    
    def display_allan_analysis(self, data_history):
        """Display Allan deviation analysis"""
        print("\n📈 ALLAN DEVIATION ANALYSIS")
        print("-" * 30)
        
        freq_data = data_history['frequency_error']
        tau_values = [1, 2, 4, 8, 16, 32]
        
        allan_data = self.calculate_allan_deviation(freq_data, tau_values)
        
        print("Tau (s) | Allan Deviation (ppm)")
        print("-" * 35)
        for point in allan_data:
            print(f"{point['tau']:7d} | {point['allan_deviation']:.6f}")
    
    def save_demo_data(self, data_history):
        """Save demo data for web interface testing"""
        demo_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_points': len(data_history['timestamps']),
                'description': 'Simulated SA5X data for graph testing'
            },
            'data': data_history
        }
        
        with open('demo_data.json', 'w') as f:
            json.dump(demo_data, f, indent=2)
        
        print(f"\n💾 Demo data saved to 'demo_data.json'")
        print("You can use this data to test the web interface graphs.")


def main():
    """Main function to run the graph demo"""
    tester = SA5XGraphTester()
    
    print("SA5X Monitor - Graph Testing Demo")
    print("This script demonstrates the graph functionality with simulated data.")
    print()
    
    try:
        # Run demo for 60 seconds with 1-second intervals
        tester.run_graph_demo(duration=60, interval=1)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {e}")


if __name__ == '__main__':
    main()