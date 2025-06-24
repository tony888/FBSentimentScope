#!/usr/bin/env python3
"""
Facebook Comment Sentiment Analyzer - Main Entry Point

A comprehensive tool for analyzing sentiment in Facebook post comments
with support for multiple languages (English and Thai).

Usage:
    python main.py analyze-post --post-id POST_ID
    python main.py analyze-page --page-id PAGE_ID
    python main.py setup
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.interfaces.cli import main

if __name__ == "__main__":
    main()
