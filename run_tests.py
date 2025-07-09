#!/usr/bin/env python3
"""
Simple test runner that executes test files with proper path setup.
Usage: python run_tests.py [test_file_name]
"""

import sys
import os
from pathlib import Path

def main():
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Get test file name from command line or use default
    test_file = sys.argv[1] if len(sys.argv) > 1 else "test_gemini_resume_parser.py"
    
    # Construct full path to test file
    test_path = project_root / "tests" / test_file
    
    if not test_path.exists():
        print(f"Test file not found: {test_path}")
        return
    
    # Execute the test file
    print(f"Running test: {test_path}")
    exec(test_path.read_text(), {'__file__': str(test_path)})

if __name__ == "__main__":
    main() 