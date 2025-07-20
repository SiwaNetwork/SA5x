#!/usr/bin/env python3
"""
SA5X Web Monitor Runner
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from web.app import SA5XWebMonitor


def main():
    parser = argparse.ArgumentParser(
        description='SA5X Web Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --host 0.0.0.0 --port 8080
  %(prog)s --debug
        """
    )
    
    parser.add_argument('--host', default='localhost',
                       help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port to bind to (default: 8080)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--config', default='config/sa5x_config.json',
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        # Create monitor instance
        monitor = SA5XWebMonitor()
        
        # Run the web application
        monitor.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        
    except KeyboardInterrupt:
        print("\nShutting down SA5X Web Monitor...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()