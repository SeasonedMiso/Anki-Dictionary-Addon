#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test runner for Anki Dictionary addon.
Can be run standalone or integrated into Anki startup.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_tests(verbose=False, coverage=False):
    """
    Run the test suite.
    
    Args:
        verbose: Show detailed output
        coverage: Generate coverage report
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        import pytest
    except ImportError:
        print("❌ pytest not installed. Install with: pip install -r requirements-test.txt")
        return 1
    
    args = ['tests/']
    
    if verbose:
        args.append('-v')
    else:
        args.append('-q')
    
    if coverage:
        args.extend(['--cov=src', '--cov-report=term-missing'])
    
    # Run tests
    print("=" * 60)
    print("Running Anki Dictionary Tests")
    print("=" * 60)
    
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code


def run_quick_tests():
    """
    Run only fast tests (for startup checks).
    
    Returns:
        True if all tests passed, False otherwise
    """
    try:
        import pytest
    except ImportError:
        return True  # Don't fail if pytest not installed
    
    # Run only fast tests
    args = ['tests/', '-q', '-m', 'not slow']
    exit_code = pytest.main(args)
    
    return exit_code == 0


def check_code_quality():
    """
    Run code quality checks.
    
    Returns:
        True if all checks passed, False otherwise
    """
    print("\n" + "=" * 60)
    print("Running Code Quality Checks")
    print("=" * 60)
    
    all_passed = True
    
    # Check with mypy (type checking)
    try:
        import mypy.api
        print("\n📝 Running mypy (type checking)...")
        result = mypy.api.run(['src/'])
        if result[2] != 0:
            print("⚠️  Type checking found issues")
            print(result[0])
            all_passed = False
        else:
            print("✅ Type checking passed")
    except ImportError:
        print("⚠️  mypy not installed, skipping type checking")
    
    return all_passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Anki Dictionary tests")
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-c', '--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('-q', '--quick', action='store_true', help='Run only quick tests')
    parser.add_argument('--quality', action='store_true', help='Run code quality checks')
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_tests()
        sys.exit(0 if success else 1)
    elif args.quality:
        success = check_code_quality()
        sys.exit(0 if success else 1)
    else:
        exit_code = run_tests(verbose=args.verbose, coverage=args.coverage)
        sys.exit(exit_code)
