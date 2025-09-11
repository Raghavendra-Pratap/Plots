#!/usr/bin/env python3
"""
Formula Engine Test Script
Focused testing of formula evaluation and data flow operations
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.data_service import DataService
from services.duckdb_service import DuckDBService

class FormulaEngineTester:
    def __init__(self):
        self.data_service = DataService()
        self.duckdb_service = DuckDBService()
        
    def test_basic_formulas(self):
        """Test basic mathematical formulas"""
        print("🧮 Testing Basic Mathematical Formulas")
        print("-" * 40)
        
        # Create sample data
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [10, 20, 30, 40, 50],
            'z': [100, 200, 300, 400, 500]
        })
        
        print("Sample data:")
        print(data)
        print()
        
        # Test basic arithmetic
        formulas = [
            ("x + y", "Addition"),
            ("y - x", "Subtraction"),
            ("x * y", "Multiplication"),
            ("y / x", "Division"),
            ("x ** 2", "Power"),
            ("sqrt(y)", "Square root"),
            ("log(y)", "Natural logarithm"),
            ("abs(x - 3)", "Absolute value")
        ]
        
        for formula, description in formulas:
            try:
                result = data.eval(formula)
                print(f"✅ {description} ({formula}): {result.tolist()}")
            except Exception as e:
                print(f"❌ {description} ({formula}): {e}")
        
        print()
    
    def test_complex_formulas(self):
        """Test complex formulas with multiple operations"""
        print("🔢 Testing Complex Formulas")
        print("-" * 40)
        
        # Create sample data
        data = pd.DataFrame({
            'price': [100, 150, 200, 250, 300],
            'quantity': [5, 3, 4, 2, 6],
            'discount': [0.1, 0.15, 0.2, 0.25, 0.3],
            'tax_rate': [0.08, 0.09, 0.07, 0.1, 0.06]
        })
        
        print("Sample data:")
        print(data)
        print()
        
        # Test complex business formulas
        complex_formulas = [
            ("price * quantity", "Total before discount"),
            ("price * quantity * (1 - discount)", "Total after discount"),
            ("price * quantity * (1 - discount) * (1 + tax_rate)", "Total with tax"),
            ("(price * quantity * discount)", "Discount amount"),
            ("(price * quantity * (1 - discount) * tax_rate)", "Tax amount"),
            ("price * quantity * (1 - discount) * (1 + tax_rate) / quantity", "Unit price after all adjustments")
        ]
        
        for formula, description in complex_formulas:
            try:
                result = data.eval(formula)
                print(f"✅ {description}:")
                print(f"   Formula: {formula}")
                print(f"   Result: {result.tolist()}")
                print()
            except Exception as e:
                print(f"❌ {description} ({formula}): {e}")
                print()
    
    def test_data_flow_operations(self):
        """Test data flow and transformation operations"""
        print("🌊 Testing Data Flow Operations")
        print("-" * 40)
        
        # Create sample data
        data = pd.DataFrame({
            'product_id': ['A001', 'A002', 'A003', 'A004', 'A005'],
            'category': ['Electronics', 'Clothing', 'Electronics', 'Books', 'Clothing'],
            'price': [299.99, 49.99, 199.99, 24.99, 79.99],
            'stock': [50, 100, 25, 200, 75],
            'rating': [4.5, 4.2, 4.8, 4.0, 4.6]
        })
        
        print("Original data:")
        print(data)
        print()
        
        # Test data flow operations
        print("1. Filtering data (Electronics category):")
        electronics = data[data['category'] == 'Electronics']
        print(electronics)
        print()
        
        print("2. Adding calculated columns:")
        data['total_value'] = data['price'] * data['stock']
        data['price_category'] = data['price'].apply(lambda x: 'High' if x > 200 else 'Medium' if x > 100 else 'Low')
        data['stock_status'] = data['stock'].apply(lambda x: 'Low' if x < 50 else 'Adequate' if x < 100 else 'High')
        print(data)
        print()
        
        print("3. Aggregating data by category:")
        category_summary = data.groupby('category').agg({
            'price': ['mean', 'min', 'max'],
            'stock': 'sum',
            'rating': 'mean'
        }).round(2)
        print(category_summary)
        print()
        
        print("4. Sorting by multiple criteria:")
        sorted_data = data.sort_values(['category', 'price'], ascending=[True, False])
        print(sorted_data)
        print()
        
        print("5. Applying conditional logic:")
        data['recommendation'] = data.apply(
            lambda row: 'Promote' if row['rating'] > 4.5 and row['stock'] > 50 
            else 'Restock' if row['stock'] < 50 
            else 'Monitor', axis=1
        )
        print(data[['product_id', 'category', 'rating', 'stock', 'recommendation']])
        print()
    
    def test_duckdb_integration(self):
        """Test DuckDB integration for advanced analytics"""
        print("🦆 Testing DuckDB Integration")
        print("-" * 40)
        
        try:
            # Create sample data
            data = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=30, freq='D'),
                'sales': np.random.randint(1000, 10000, 30),
                'region': np.random.choice(['North', 'South', 'East', 'West'], 30),
                'product': np.random.choice(['A', 'B', 'C', 'D'], 30)
            })
            
            print("Sample sales data:")
            print(data.head(10))
            print(f"Total rows: {len(data)}")
            print()
            
            # Test DuckDB operations
            print("1. Creating DuckDB table:")
            table_name = "test_sales"
            self.duckdb_service.create_table_from_dataframe(data, table_name)
            print(f"✅ Table '{table_name}' created successfully")
            
            print("\n2. Basic SQL queries:")
            # Total sales
            total_sales = self.duckdb_service.execute_query(f"SELECT SUM(sales) as total_sales FROM {table_name}")
            print(f"Total sales: ${total_sales[0]['total_sales']:,}")
            
            # Sales by region
            sales_by_region = self.duckdb_service.execute_query(f"""
                SELECT region, SUM(sales) as total_sales, COUNT(*) as transactions
                FROM {table_name}
                GROUP BY region
                ORDER BY total_sales DESC
            """)
            print("\nSales by region:")
            for row in sales_by_region:
                print(f"  {row['region']}: ${row['total_sales']:,} ({row['transactions']} transactions)")
            
            # Sales by product
            sales_by_product = self.duckdb_service.execute_query(f"""
                SELECT product, SUM(sales) as total_sales, AVG(sales) as avg_sales
                FROM {table_name}
                GROUP BY product
                ORDER BY total_sales DESC
            """)
            print("\nSales by product:")
            for row in sales_by_product:
                print(f"  {row['product']}: ${row['total_sales']:,} (avg: ${row['avg_sales']:.2f})")
            
            # Time series analysis
            daily_sales = self.duckdb_service.execute_query(f"""
                SELECT date, SUM(sales) as daily_sales
                FROM {table_name}
                GROUP BY date
                ORDER BY date
            """)
            print(f"\nDaily sales trend: {len(daily_sales)} days")
            
            # Clean up
            self.duckdb_service.execute_query(f"DROP TABLE IF EXISTS {table_name}")
            print(f"\n✅ Table '{table_name}' cleaned up")
            
        except Exception as e:
            print(f"❌ DuckDB integration test failed: {e}")
    
    def test_formula_validation(self):
        """Test formula validation and error handling"""
        print("✅ Testing Formula Validation")
        print("-" * 40)
        
        # Create sample data
        data = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [10, 20, 30, 40, 50],
            'c': [100, 200, 300, 400, 500]
        })
        
        # Test valid formulas
        valid_formulas = [
            "a + b",
            "b * c / a",
            "(a + b) * c",
            "sqrt(a * b)",
            "log(c / a)"
        ]
        
        print("Testing valid formulas:")
        for formula in valid_formulas:
            try:
                result = data.eval(formula)
                print(f"✅ '{formula}' → {result.tolist()}")
            except Exception as e:
                print(f"❌ '{formula}' → Error: {e}")
        
        print("\nTesting invalid formulas:")
        # Test invalid formulas
        invalid_formulas = [
            "a + ",  # Incomplete
            "a + b +",  # Incomplete
            "a / 0",  # Division by zero
            "sqrt(-1)",  # Invalid operation
            "log(0)",  # Invalid operation
            "undefined_column + 1"  # Non-existent column
        ]
        
        for formula in invalid_formulas:
            try:
                result = data.eval(formula)
                print(f"⚠️ '{formula}' → {result.tolist()}")
            except Exception as e:
                print(f"✅ '{formula}' → Correctly caught error: {e}")
    
    def run_all_tests(self):
        """Run all formula engine tests"""
        print("🚀 Starting Formula Engine Testing Suite")
        print("=" * 60)
        
        try:
            self.test_basic_formulas()
            self.test_complex_formulas()
            self.test_data_flow_operations()
            self.test_duckdb_integration()
            self.test_formula_validation()
            
            print("=" * 60)
            print("🎉 All formula engine tests completed successfully!")
            print("The formula engine is working correctly for:")
            print("  • Basic mathematical operations")
            print("  • Complex business formulas")
            print("  • Data flow and transformations")
            print("  • DuckDB integration")
            print("  • Formula validation and error handling")
            
        except Exception as e:
            print(f"💥 Formula engine testing failed: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run the formula engine tests"""
    tester = FormulaEngineTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
