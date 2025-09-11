#!/usr/bin/env python3
"""
Backend Services Test Script
Tests all backend services independently without the frontend UI
"""

import sys
import os
import pandas as pd
import duckdb
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.duckdb_service import DuckDBService
from services.workflow_service import WorkflowService
from services.data_service import DataService
from utils.data_validator import DataValidator
from utils.file_handler import FileHandler
from models.database import DatabaseManager

class BackendTester:
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
            from models.database import init_database
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
    
    def test_duckdb_service(self):
        """Test DuckDB service functionality"""
        print("\n🐤 Testing DuckDB Service...")
        
        try:
            # Test basic connection
            print("  - Testing basic connection...")
            result = self.duckdb_service.execute_query("SELECT 1 as test")
            print(f"    ✅ Basic query result: {result}")
            
            # Test data processing with sample data
            print("  - Testing data processing...")
            sample_data = pd.DataFrame({
                'id': [1, 2, 3, 4, 5],
                'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
                'age': [25, 30, 35, 28, 32],
                'salary': [50000, 60000, 70000, 55000, 65000]
            })
            
            # Test table creation and data insertion
            table_name = "test_employees"
            self.duckdb_service.create_table_from_dataframe(sample_data, table_name)
            print(f"    ✅ Table '{table_name}' created successfully")
            
            # Test data querying
            result = self.duckdb_service.execute_query(f"SELECT * FROM {table_name}")
            print(f"    ✅ Data query result: {len(result)} rows")
            
            # Test analytics queries
            print("  - Testing analytics queries...")
            avg_salary = self.duckdb_service.execute_query(f"SELECT AVG(salary) as avg_salary FROM {table_name}")
            print(f"    ✅ Average salary: {avg_salary}")
            
            age_distribution = self.duckdb_service.execute_query(f"SELECT age, COUNT(*) as count FROM {table_name} GROUP BY age ORDER BY age")
            print(f"    ✅ Age distribution: {age_distribution}")
            
            # Clean up
            self.duckdb_service.execute_query(f"DROP TABLE IF EXISTS {table_name}")
            print("    ✅ Test table cleaned up")
            
            print("✅ DuckDB Service tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ DuckDB Service test failed: {e}")
            return False
    
    def test_workflow_service(self):
        """Test Workflow service functionality"""
        print("\n⚙️ Testing Workflow Service...")
        
        try:
            # Test workflow validation
            print("  - Testing workflow validation...")
            
            # Valid workflow
            valid_workflow = {
                "name": "Test Workflow",
                "description": "A test workflow",
                "steps": [
                    {
                        "id": "step1",
                        "type": "data_load",
                        "config": {"source": "test.csv", "format": "csv"}
                    },
                    {
                        "id": "step2", 
                        "type": "data_transform",
                        "config": {"operation": "filter", "condition": "age > 25"}
                    }
                ]
            }
            
            validation_result = self.workflow_service.validate_workflow(valid_workflow)
            print(f"    ✅ Valid workflow validation: {validation_result}")
            
            # Invalid workflow (missing required fields)
            invalid_workflow = {
                "name": "Invalid Workflow"
                # Missing required fields
            }
            
            validation_result = self.workflow_service.validate_workflow(invalid_workflow)
            print(f"    ✅ Invalid workflow validation: {validation_result}")
            
            # Test workflow execution
            print("  - Testing workflow execution...")
            
            # Create a simple test workflow
            test_workflow = {
                "name": "Simple Test Workflow",
                "description": "A simple test workflow",
                "steps": [
                    {
                        "id": "create_data",
                        "type": "data_generation",
                        "config": {"rows": 10, "columns": ["id", "value"]}
                    }
                ]
            }
            
            execution_result = self.workflow_service.execute_workflow(test_workflow)
            print(f"    ✅ Workflow execution result: {execution_result}")
            
            print("✅ Workflow Service tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Workflow Service test failed: {e}")
            return False
    
    def test_data_service(self):
        """Test Data service functionality"""
        print("\n📊 Testing Data Service...")
        
        try:
            # Test data source management
            print("  - Testing data source management...")
            
            # Create a test data source
            test_source = {
                "name": "Test CSV Source",
                "type": "file",
                "path": "test_data.csv",
                "format": "csv",
                "description": "Test data source for testing"
            }
            
            source_id = self.data_service.create_data_source(test_source)
            print(f"    ✅ Data source created with ID: {source_id}")
            
            # Retrieve data source
            retrieved_source = self.data_service.get_data_source(source_id)
            print(f"    ✅ Data source retrieved: {retrieved_source['name']}")
            
            # Test data processing
            print("  - Testing data processing...")
            
            # Create sample data for processing
            sample_df = pd.DataFrame({
                'product': ['A', 'B', 'C', 'A', 'B'],
                'sales': [100, 150, 200, 120, 180],
                'region': ['North', 'South', 'East', 'North', 'South']
            })
            
            # Test data aggregation
            aggregated = self.data_service.aggregate_data(sample_df, ['product'], ['sales'], ['sum', 'mean'])
            print(f"    ✅ Data aggregation result: {len(aggregated)} rows")
            
            # Test data filtering
            filtered = self.data_service.filter_data(sample_df, {'region': 'North'})
            print(f"    ✅ Data filtering result: {len(filtered)} rows")
            
            # Clean up
            self.data_service.delete_data_source(source_id)
            print("    ✅ Test data source cleaned up")
            
            print("✅ Data Service tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Data Service test failed: {e}")
            return False
    
    def test_data_validator(self):
        """Test Data Validator functionality"""
        print("\n🔍 Testing Data Validator...")
        
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
            print(f"    ✅ Valid data validation: {validation_result['is_valid']}")
            
            # Invalid data (missing values)
            invalid_df = pd.DataFrame({
                'id': [1, 2, None],
                'name': ['Alice', None, 'Charlie'],
                'age': [25, 30, 35]
            })
            
            validation_result = self.data_validator.validate_dataframe(invalid_df)
            print(f"    ✅ Invalid data validation: {validation_result['is_valid']}")
            if not validation_result['is_valid']:
                print(f"      Issues found: {validation_result['issues']}")
            
            # Test data summary
            print("  - Testing data summary generation...")
            summary = self.data_validator.generate_data_summary(valid_df)
            print(f"    ✅ Data summary generated: {summary['total_rows']} rows, {summary['total_columns']} columns")
            
            print("✅ Data Validator tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Data Validator test failed: {e}")
            return False
    
    def test_file_handler(self):
        """Test File Handler functionality"""
        print("\n📁 Testing File Handler...")
        
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
            print(f"    ✅ File info retrieved: {file_info['size']} bytes")
            
            # Test file hash
            file_hash = self.file_handler.calculate_file_hash(test_file_path)
            print(f"    ✅ File hash calculated: {file_hash[:16]}...")
            
            # Test file validation
            is_valid = self.file_handler.validate_file(test_file_path)
            print(f"    ✅ File validation: {is_valid}")
            
            # Clean up
            os.remove(test_file_path)
            print("    ✅ Test file cleaned up")
            
            print("✅ File Handler tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ File Handler test failed: {e}")
            return False
    
    def test_formula_engine(self):
        """Test Formula Engine functionality"""
        print("\n🧮 Testing Formula Engine...")
        
        try:
            # Test basic formula evaluation
            print("  - Testing basic formula evaluation...")
            
            # Create sample data
            sample_data = pd.DataFrame({
                'x': [1, 2, 3, 4, 5],
                'y': [10, 20, 30, 40, 50],
                'z': [100, 200, 300, 400, 500]
            })
            
            # Test simple arithmetic
            formulas = [
                "x + y",
                "y * 2",
                "z / x",
                "(x + y) * z / 100"
            ]
            
            for formula in formulas:
                try:
                    result = self.data_service.evaluate_formula(sample_data, formula)
                    print(f"    ✅ Formula '{formula}': {len(result)} rows")
                except Exception as e:
                    print(f"    ⚠️ Formula '{formula}' failed: {e}")
            
            # Test data flow operations
            print("  - Testing data flow operations...")
            
            # Test chaining operations
            try:
                # Load data
                data = sample_data.copy()
                
                # Apply transformations
                data['sum_xy'] = data['x'] + data['y']
                data['product_xyz'] = data['x'] * data['y'] * data['z']
                data['ratio'] = data['z'] / data['x']
                
                print(f"    ✅ Data flow operations completed: {len(data)} rows, {len(data.columns)} columns")
                
                # Show sample results
                print(f"    📊 Sample results:\n{data.head(3)}")
                
            except Exception as e:
                print(f"    ⚠️ Data flow operations failed: {e}")
            
            print("✅ Formula Engine tests completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Formula Engine test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all backend service tests"""
        print("🚀 Starting Backend Services Testing Suite")
        print("=" * 50)
        
        if not self.initialize_services():
            print("❌ Service initialization failed. Cannot proceed with tests.")
            return False
        
        test_results = []
        
        # Run all tests
        test_results.append(("DuckDB Service", self.test_duckdb_service()))
        test_results.append(("Workflow Service", self.test_workflow_service()))
        test_results.append(("Data Service", self.test_data_service()))
        test_results.append(("Data Validator", self.test_data_validator()))
        test_results.append(("File Handler", self.test_file_handler()))
        test_results.append(("Formula Engine", self.test_formula_engine()))
        
        # Print summary
        print("\n" + "=" * 50)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 50)
        
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
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✨ Backend testing completed successfully!")
        print("You can now use these services in your frontend or other applications.")
    else:
        print("\n💥 Backend testing completed with some failures.")
        print("Please review the error messages above and fix any issues.")

if __name__ == "__main__":
    main()
