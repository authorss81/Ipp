#!/usr/bin/env python3
"""CLI entry point for ipp-lang package."""

import sys
import os

def main():
    """Main CLI entry point."""
    from ipp import main as ipp_main
    sys.exit(ipp_main.main())

if __name__ == "__main__":
    main()
