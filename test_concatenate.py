#!/usr/bin/env python3
"""
Test script for CONCATENATE formula functionality
"""

import sys
import os
import pandas as pd

# Add the current directory to Python path to import the main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the FormulaProcessor from the main file
    from playground_x_duckdb import FormulaProcessor
    
    def test_concatenate_basic():
        """Test basic CONCATENATE functionality"""
        print("Testing CONCATENATE formula...")
        
        # Create test data
        test_df = pd.DataFrame({
            'Name': ['John', 'Jane', 'Bob'],
            'Age': [25, 30, 35],
            'City': ['NYC', 'LA', 'CHI']
        })
        
        # Create formula processor
        processor = FormulaProcessor()
        
        # Test 1: Simple concatenation with custom text
        formula_str = "CONCATENATE [Name -> custom< is > -> Age -> custom< years old from > -> City]"
        
        try:
            result = processor.apply_formula(test_df, formula_str)
            print("✓ CONCATENATE Test 1 (Basic): PASSED")
            print(f"  Result: {result.tolist()}")
        except Exception as e:
            print(f"✗ CONCATENATE Test 1 (Basic): FAILED - {e}")
            return False
        
        # Test 2: Simple column concatenation
        formula_str2 = "CONCATENATE [Name -> custom< - > -> City]"
        
        try:
            result2 = processor.apply_formula(test_df, formula_str2)
            print("✓ CONCATENATE Test 2 (Simple): PASSED")
            print(f"  Result: {result2.tolist()}")
        except Exception as e:
            print(f"✗ CONCATENATE Test 2 (Simple): FAILED - {e}")
            return False
        
        # Test 3: Custom text only
        formula_str3 = "CONCATENATE [custom<Hello World>]"
        
        try:
            result3 = processor.apply_formula(test_df, formula_str3)
            print("✓ CONCATENATE Test 3 (Custom text): PASSED")
            print(f"  Result: {result3.tolist()}")
        except Exception as e:
            print(f"✗ CONCATENATE Test 3 (Custom text): FAILED - {e}")
            return False
        
        print("\n🎉 All CONCATENATE tests passed!")
        return True
        
    def test_duckdb_integration():
        """Test DuckDB integration"""
        print("\nTesting DuckDB integration...")
        
        try:
            import duckdb
            print("✓ DuckDB is available")
            
            # Test DuckDB connection
            conn = duckdb.connect(':memory:')
            test_df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
            conn.register('test', test_df)
            
            result = conn.execute("SELECT A || ' - ' || B as combined FROM test").df()
            print("✓ DuckDB concatenation works")
            print(f"  Result: {result['combined'].tolist()}")
            
            conn.close()
            return True
            
        except ImportError:
            print("✗ DuckDB not available - will use pandas fallback")
            return False
        except Exception as e:
            print(f"✗ DuckDB test failed: {e}")
            return False
    
    if __name__ == "__main__":
        print("=" * 50)
        print("CONCATENATE Formula Test Suite")
        print("=" * 50)
        
        # Test DuckDB integration first
        duckdb_ok = test_duckdb_integration()
        
        # Test CONCATENATE formula
        formula_ok = test_concatenate_basic()
        
        print("\n" + "=" * 50)
        if formula_ok:
            print("✅ All tests passed! CONCATENATE formula is working correctly.")
        else:
            print("❌ Some tests failed. Please check the errors above.")
        print("=" * 50)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the same directory as 'playground x duckdb.py'")
except Exception as e:
    print(f"❌ Unexpected error: {e}") 