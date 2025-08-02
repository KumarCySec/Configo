#!/usr/bin/env python3
"""
CONFIGO - Autonomous AI Setup Agent
==================================

Main entry point for CONFIGO CLI application.
This file serves as the primary entry point for the CONFIGO command-line interface.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the main CLI application
from cli.main import main

if __name__ == "__main__":
    main() 