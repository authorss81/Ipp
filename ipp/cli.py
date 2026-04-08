#!/usr/bin/env python3
"""CLI entry point for ipp-lang package."""

import sys
import os

def main():
    """Main CLI entry point."""
    # Import the main module from the project root
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Import and run the CLI
    import main as ipp_main
    sys.exit(ipp_main.main())

if __name__ == "__main__":
    main()
