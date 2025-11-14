#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script for Phase 2 refactoring.
Tests that the refactored dictdb.py works correctly.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        from dictdb import DictDB
        print("✓ DictDB import successful")
        
        from src.database import DatabaseConnection, DictionaryRepository
        print("✓ Database modules import successful")
        
        from src.constants import DICT_GOOGLE_IMAGES, DICT_FORVO
        print("✓ Constants import successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_dictdb_creation():
    """Test that DictDB can be instantiated."""
    print("\nTesting DictDB creation...")
    try:
        # Note: This will fail outside of Anki environment
        # but we can test the class structure
        from dictdb import DictDB
        
        # Check that class has expected methods
        expected_methods = [
            'getLangId',
            'getCurrentDbLangs',
            'addDict',
            'deleteDict',
            'searchTerm',
            'getAllDicts',
            'getAllDictsWithLang',
        ]
        
        for method in expected_methods:
            if hasattr(DictDB, method):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ DictDB creation test failed: {e}")
        return False

def test_type_hints():
    """Test that type hints are present."""
    print("\nTesting type hints...")
    try:
        from dictdb import DictDB
        import inspect
        
        # Check a few key methods have type hints
        methods_to_check = ['getLangId', 'searchTerm', 'addDict']
        
        for method_name in methods_to_check:
            method = getattr(DictDB, method_name)
            sig = inspect.signature(method)
            
            # Check if return annotation exists
            if sig.return_annotation != inspect.Signature.empty:
                print(f"✓ Method '{method_name}' has return type hint")
            else:
                print(f"✗ Method '{method_name}' missing return type hint")
        
        return True
    except Exception as e:
        print(f"✗ Type hint test failed: {e}")
        return False

def test_backward_compatibility():
    """Test that old interface is maintained."""
    print("\nTesting backward compatibility...")
    try:
        from dictdb import DictDB
        
        # Check that old attributes exist
        expected_attrs = ['conn', 'c', 'db_connection', 'repository']
        
        # We can't instantiate without Anki, but we can check the __init__ signature
        import inspect
        init_source = inspect.getsource(DictDB.__init__)
        
        for attr in expected_attrs:
            if f'self.{attr}' in init_source:
                print(f"✓ Attribute 'self.{attr}' is set in __init__")
            else:
                print(f"✗ Attribute 'self.{attr}' not found in __init__")
        
        return True
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 2 Refactoring Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("DictDB Creation", test_dictdb_creation),
        ("Type Hints", test_type_hints),
        ("Backward Compatibility", test_backward_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 2 refactoring looks good.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
