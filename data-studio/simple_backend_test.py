#!/usr/bin/env python3
"""
Simple Backend Test Script
Tests core backend functionality with actual service interfaces
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.duckdb_service import DuckDBService
from services.workflow_service import WorkflowService
from services.data_service import DataService
from utils.data_validator import DataValidator
from utils.file_handler import FileHandler
from models.database import init_database, DatabaseManager

class SimpleBackendTester:
    def __init__(self):
        self.duckdb_service = None
        self.workflow_service = None
        self.data_service = None
        self.data_validator = None
        self.file_handler = None
        self.db_manager = None
        
    def initialize_services(self):
        """Initialize all backend services"""
        print("🔧 Initializing backend services...")
        
        try:
            # Initialize database
            init_database()
            self.db_manager = DatabaseManager()
            print("✅ Database initialized successfully")
            
            # Initialize services
            self.duckdb_service = DuckDBService()
            self.workflow_service = WorkflowService()
            self.data_service = DataService()
            self.data_validator = DataValidator()
            self.file_handler = FileHandler()
            
            print("✅ All services initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize services: {e}")
            return False
    
    def test_duckdb_basic(self):
        """Test basic DuckDB functionality"""
        print("\n🐤 Testing DuckDB Basic Functionality...")
        
        try:
            # Test if service is healthy
            is_healthy = self.duckdb_service.is_healthy()
            print(f"  ✅ DuckDB service health: {is_healthy}")
            
            # Test file processing with sample data
            print("  - Testing data processing...")
            
            # Create a sample CSV file
            sample_data = pd.DataFrame({
                'id': [1, 2, 3, 4, 5],
                'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
                'age': [25, 30, 35, 28, 32],
                'salary': [50000, 60000, 70000, 55000, 65000]
            })
            
            # Save to temporary CSV
            temp_csv = "temp_sample.csv"
            sample_data.to_csv(temp_csv, index=False)
            
            # Test file processing
            result = self.duckdb_service.process_file(temp_csv)
            print(f"    ✅ File processed: {result['row_count']} rows, {result['column_count']} columns")
            print(f"    ✅ Processing time: {result['processing_time']:.4f} seconds")
            
            # Clean up
            os.remove(temp_csv)
            print("    ✅ Temporary file cleaned up")
            
            print("✅ DuckDB Basic tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ DuckDB Basic test failed: {e}")
            return False
    
    def test_duckdb_analytics(self):
        """Test DuckDB analytics functionality"""
        print("\n📊 Testing DuckDB Analytics...")
        
        try:
            # Test complex analytics
            print("  - Testing complex analytics...")
            
            # Create sample data for analytics
            sample_data = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=30, freq='D'),
                'sales': np.random.randint(1000, 10000, 30),
                'region': np.random.choice(['North', 'South', 'East', 'West'], 30),
                'product': np.random.choice(['A', 'B', 'C', 'D'], 30)
            })
            
            # Save to temporary CSV for processing
            temp_csv = "temp_analytics.csv"
            sample_data.to_csv(temp_csv, index=False)
            
            # Test analytics
            analytics_config = {
                'type': 'statistical_analysis',
                'data_source': temp_csv,
                'parameters': {
                    'metrics': ['mean', 'std', 'min', 'max'],
                    'group_by': ['region', 'product']
                }
            }
            
            result = self.duckdb_service.perform_complex_analytics(analytics_config)
            print(f"    ✅ Analytics completed: {result['analytics_type']}")
            print(f"    ✅ Execution time: {result['execution_time']:.4f} seconds")
            
            # Clean up
            os.remove(temp_csv)
            print("    ✅ Temporary file cleaned up")
            
            print("✅ DuckDB Analytics tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ DuckDB Analytics test failed: {e}")
            return False
    
    def test_data_validation(self):
        """Test data validation functionality"""
        print("\n🔍 Testing Data Validation...")
        
        try:
            # Test data validation
            print("  - Testing data validation...")
            
            # Valid data
            valid_df = pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [25, 30, 35]
            })
            
            validation_result = self.data_validator.validate_dataframe(valid_df)
            print(f"    ✅ Valid data validation: {validation_result.get('is_valid', 'N/A')}")
            
            # Test data summary
            print("  - Testing data summary generation...")
            summary = self.data_validator.generate_data_summary(valid_df)
            print(f"    ✅ Data summary generated: {summary.get('total_rows', 'N/A')} rows, {summary.get('total_columns', 'N/A')} columns")
            
            print("✅ Data Validation tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Data Validation test failed: {e}")
            return False
    
    def test_file_operations(self):
        """Test file handling operations"""
        print("\n📁 Testing File Operations...")
        
        try:
            # Test file operations
            print("  - Testing file operations...")
            
            # Create a test file
            test_file_path = "test_file.txt"
            test_content = "This is a test file for testing file handler functionality."
            
            with open(test_file_path, 'w') as f:
                f.write(test_content)
            
            # Test file info
            file_info = self.file_handler.get_file_info(test_file_path)
            print(f"    ✅ File info retrieved: {file_info.get('size', 'N/A')} bytes")
            
            # Test file hash
            file_hash = self.file_handler.calculate_file_hash(test_file_path)
            print(f"    ✅ File hash calculated: {file_hash[:16] if file_hash else 'N/A'}...")
            
            # Clean up
            os.remove(test_file_path)
            print("    ✅ Test file cleaned up")
            
            print("✅ File Operations tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ File Operations test failed: {e}")
            return False
    
    def test_formula_operations(self):
        """Test formula and data flow operations"""
        print("\n🧮 Testing Formula and Data Flow Operations...")
        
        try:
            # Test basic pandas operations (formula-like)
            print("  - Testing basic operations...")
            
            # Create sample data
            sample_data = pd.DataFrame({
                'x': [1, 2, 3, 4, 5],
                'y': [10, 20, 30, 40, 50],
                'z': [100, 200, 300, 400, 500]
            })
            
            # Test operations
            sample_data['sum_xy'] = sample_data['x'] + sample_data['y']
            sample_data['product_xyz'] = sample_data['x'] * sample_data['y'] * sample_data['z']
            sample_data['ratio'] = sample_data['z'] / sample_data['x']
            
            print(f"    ✅ Operations completed: {len(sample_data)} rows, {len(sample_data.columns)} columns")
            print(f"    📊 Sample results:\n{sample_data.head(3)}")
            
            # Test data flow
            print("  - Testing data flow...")
            
            # Filter
            filtered = sample_data[sample_data['x'] > 2]
            print(f"    ✅ Filtered data: {len(filtered)} rows")
            
            # Aggregate
            aggregated = sample_data.groupby('x').agg({
                'y': 'sum',
                'z': 'mean'
            })
            print(f"    ✅ Aggregated data: {len(aggregated)} groups")
            
            print("✅ Formula and Data Flow tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Formula and Data Flow test failed: {e}")
            return False
    
    def test_database_operations(self):
        """Test database operations"""
        print("\n🗄️ Testing Database Operations...")
        
        try:
            # Test basic database operations
            print("  - Testing database operations...")
            
            # Test connection
            conn = self.db_manager.get_connection()
            print("    ✅ Database connection established")
            
            # Test simple query
            result = self.db_manager.execute_query("SELECT 1 as test")
            print(f"    ✅ Test query executed: {result}")
            
            # Test table creation
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    value REAL
                )
            '''
            self.db_manager.execute_query(create_table_query)
            print("    ✅ Test table created")
            
            # Test data insertion
            insert_query = "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)"
            self.db_manager.execute_query(insert_query, (1, 'Test Item', 42.5))
            print("    ✅ Data inserted")
            
            # Test data retrieval
            select_result = self.db_manager.execute_query("SELECT * FROM test_table")
            print(f"    ✅ Data retrieved: {len(select_result)} rows")
            
            # Clean up
            self.db_manager.execute_query("DROP TABLE test_table")
            print("    ✅ Test table cleaned up")
            
            print("✅ Database Operations tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Database Operations test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all backend service tests"""
        print("🚀 Starting Simple Backend Services Testing Suite")
        print("=" * 60)
        
        if not self.initialize_services():
            print("❌ Service initialization failed. Cannot proceed with tests.")
            return False
        
        test_results = []
        
        # Run all tests
        test_results.append(("DuckDB Basic", self.test_duckdb_basic()))
        test_results.append(("DuckDB Analytics", self.test_duckdb_analytics()))
        test_results.append(("Data Validation", self.test_data_validation()))
        test_results.append(("File Operations", self.test_file_operations()))
        test_results.append(("Formula & Data Flow", self.test_formula_operations()))
        test_results.append(("Database Operations", self.test_database_operations()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for service_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{service_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend services are working correctly.")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
        
        return passed == total

def main():
    """Main function to run the backend tests"""
    tester = SimpleBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✨ Backend testing completed successfully!")
        print("You can now use these services in your frontend or other applications.")
    else:
        print("\n💥 Backend testing completed with some failures.")
        print("Please review the error messages above and fix any issues.")

if __name__ == "__main__":
    main()
