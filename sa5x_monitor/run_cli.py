#!/usr/bin/env python3
"""
SA5X CLI Monitor Runner
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from cli.main import main

if __name__ == '__main__':
    main()