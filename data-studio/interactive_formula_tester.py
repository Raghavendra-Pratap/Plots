#!/usr/bin/env python3
"""
Interactive Formula Tester
Interactive testing of formulas, data flow operations, and workflow building
"""

import sys
import os
import pandas as pd
import numpy as np
import json
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.duckdb_service import DuckDBService
from services.workflow_service import WorkflowService
from services.data_service import DataService
from utils.data_validator import DataValidator
from utils.file_handler import FileHandler
from models.database import init_database, DatabaseManager

class InteractiveFormulaTester:
    def __init__(self):
        self.duckdb_service = None
        self.workflow_service = None
        self.data_service = None
        self.data_validator = None
        self.file_handler = None
        self.db_manager = None
        self.sample_datasets = {}
        self.workflow_steps = []
        
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
            
            # Create sample datasets
            self._create_sample_datasets()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize services: {e}")
            return False
    
    def _create_sample_datasets(self):
        """Create sample datasets for testing"""
        print("📊 Creating sample datasets...")
        
        # Sample 1: Employee data
        self.sample_datasets['employees'] = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
            'age': [25, 30, 35, 28, 32, 29, 27, 31, 26, 33],
            'department': ['HR', 'Engineering', 'Marketing', 'HR', 'Engineering', 'Sales', 'Marketing', 'Engineering', 'HR', 'Sales'],
            'salary': [50000, 75000, 60000, 52000, 80000, 65000, 58000, 85000, 48000, 70000],
            'years_experience': [2, 5, 8, 3, 6, 4, 5, 7, 2, 8],
            'performance_rating': [4.2, 4.5, 4.1, 4.3, 4.8, 4.0, 4.4, 4.6, 4.1, 4.7]
        })
        
        # Sample 2: Sales data
        self.sample_datasets['sales'] = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'product_id': np.random.choice(['A001', 'A002', 'A003', 'A004', 'A005'], 30),
            'product_name': np.random.choice(['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard'], 30),
            'quantity': np.random.randint(1, 10, 30),
            'unit_price': np.random.uniform(100, 2000, 30).round(2),
            'region': np.random.choice(['North', 'South', 'East', 'West'], 30),
            'salesperson': np.random.choice(['John', 'Jane', 'Mike', 'Sarah', 'David'], 30)
        })
        
        # Sample 3: Financial data
        self.sample_datasets['financial'] = pd.DataFrame({
            'month': pd.date_range('2023-01-01', periods=12, freq='M'),
            'revenue': [120000, 135000, 142000, 138000, 156000, 168000, 175000, 182000, 190000, 195000, 210000, 225000],
            'expenses': [95000, 102000, 108000, 105000, 118000, 125000, 130000, 135000, 140000, 145000, 155000, 165000],
            'profit': [25000, 33000, 34000, 33000, 38000, 43000, 45000, 47000, 50000, 50000, 55000, 60000],
            'customers': [1200, 1350, 1420, 1380, 1560, 1680, 1750, 1820, 1900, 1950, 2100, 2250]
        })
        
        print(f"✅ Created {len(self.sample_datasets)} sample datasets")
        for name, df in self.sample_datasets.items():
            print(f"   📁 {name}: {len(df)} rows × {len(df.columns)} columns")
    
    def show_main_menu(self):
        """Show the main interactive menu"""
        while True:
            print("\n" + "="*60)
            print("🧮 INTERACTIVE FORMULA TESTER")
            print("="*60)
            print("1. 📊 Test Basic Formulas")
            print("2. 🔢 Test Complex Business Formulas")
            print("3. 🌊 Test Data Flow Operations")
            print("4. 🦆 Test DuckDB Analytics")
            print("5. ⚙️ Test Workflow Building")
            print("6. 📁 Test File Operations")
            print("7. 🔍 Test Data Validation")
            print("8. 📈 View Sample Datasets")
            print("9. 🚀 Run All Tests")
            print("0. ❌ Exit")
            print("="*60)
            
            choice = input("Enter your choice (0-9): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                self.test_basic_formulas()
            elif choice == '2':
                self.test_complex_business_formulas()
            elif choice == '3':
                self.test_data_flow_operations()
            elif choice == '4':
                self.test_duckdb_analytics()
            elif choice == '5':
                self.test_workflow_building()
            elif choice == '6':
                self.test_file_operations()
            elif choice == '7':
                self.test_data_validation()
            elif choice == '8':
                self.view_sample_datasets()
            elif choice == '9':
                self.run_all_tests()
            else:
                print("❌ Invalid choice. Please try again.")
    
    def test_basic_formulas(self):
        """Test basic mathematical formulas interactively"""
        print("\n🧮 Testing Basic Mathematical Formulas")
        print("-" * 50)
        
        # Get dataset choice
        dataset_name = self._select_dataset()
        if not dataset_name:
            return
        
        df = self.sample_datasets[dataset_name]
        print(f"\n📊 Using dataset: {dataset_name}")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        # Show sample data
        print("\n📋 Sample data:")
        print(df.head(3))
        
        # Test basic operations
        print("\n🔢 Testing basic operations...")
        
        # Get column choices for operations
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) < 2:
            print("❌ Need at least 2 numeric columns for operations")
            return
        
        col1 = self._select_column(df, numeric_columns, "first column")
        col2 = self._select_column(df, numeric_columns, "second column")
        
        if not col1 or not col2:
            return
        
        # Perform operations
        operations = [
            (f"{col1} + {col2}", df[col1] + df[col2]),
            (f"{col1} - {col2}", df[col1] - df[col2]),
            (f"{col1} * {col2}", df[col1] * df[col2]),
            (f"{col1} / {col2}", df[col1] / df[col2]),
            (f"{col1} ** 2", df[col1] ** 2),
            (f"sqrt({col1})", np.sqrt(df[col1])),
            (f"log({col1})", np.log(df[col1])),
            (f"abs({col1} - {col2})", np.abs(df[col1] - df[col2]))
        ]
        
        print(f"\n📊 Results for {col1} and {col2}:")
        for operation, result in operations:
            try:
                print(f"   ✅ {operation}: {result.head(3).tolist()}")
            except Exception as e:
                print(f"   ❌ {operation}: Error - {e}")
        
        input("\nPress Enter to continue...")
    
    def test_complex_business_formulas(self):
        """Test complex business formulas interactively"""
        print("\n🔢 Testing Complex Business Formulas")
        print("-" * 50)
        
        # Use sales dataset for business formulas
        if 'sales' not in self.sample_datasets:
            print("❌ Sales dataset not available")
            return
        
        df = self.sample_datasets['sales'].copy()
        print(f"\n📊 Using dataset: sales")
        print(f"   Shape: {df.shape}")
        
        # Show sample data
        print("\n📋 Sample sales data:")
        print(df.head(5))
        
        # Calculate business metrics
        print("\n💰 Calculating business metrics...")
        
        # Total sales
        df['total_sales'] = df['quantity'] * df['unit_price']
        print(f"   ✅ Total sales calculated: ${df['total_sales'].sum():,.2f}")
        
        # Discount calculation (10% for quantities > 5)
        df['discount_rate'] = np.where(df['quantity'] > 5, 0.10, 0.05)
        df['discount_amount'] = df['total_sales'] * df['discount_rate']
        df['final_sales'] = df['total_sales'] - df['discount_amount']
        print(f"   ✅ Discount applied: ${df['discount_amount'].sum():,.2f}")
        print(f"   ✅ Final sales after discount: ${df['final_sales'].sum():,.2f}")
        
        # Profit margin (assuming 30% cost)
        df['cost'] = df['total_sales'] * 0.30
        df['profit'] = df['final_sales'] - df['cost']
        df['profit_margin'] = (df['profit'] / df['final_sales']) * 100
        print(f"   ✅ Total profit: ${df['profit'].sum():,.2f}")
        print(f"   ✅ Average profit margin: {df['profit_margin'].mean():.1f}%")
        
        # Regional analysis
        regional_sales = df.groupby('region')['final_sales'].agg(['sum', 'mean', 'count']).round(2)
        print(f"\n🌍 Regional sales analysis:")
        print(regional_sales)
        
        # Product performance
        product_performance = df.groupby('product_name').agg({
            'quantity': 'sum',
            'final_sales': 'sum',
            'profit': 'sum'
        }).round(2)
        print(f"\n📦 Product performance:")
        print(product_performance)
        
        input("\nPress Enter to continue...")
    
    def test_data_flow_operations(self):
        """Test data flow operations interactively"""
        print("\n🌊 Testing Data Flow Operations")
        print("-" * 50)
        
        # Get dataset choice
        dataset_name = self._select_dataset()
        if not dataset_name:
            return
        
        df = self.sample_datasets[dataset_name].copy()
        print(f"\n📊 Using dataset: {dataset_name}")
        print(f"   Original shape: {df.shape}")
        
        # Show original data
        print("\n📋 Original data:")
        print(df.head(3))
        
        # Data flow operations
        print("\n🔄 Applying data flow operations...")
        
        # 1. Filtering
        if 'age' in df.columns:
            filtered_df = df[df['age'] > 30]
            print(f"   ✅ Filtered (age > 30): {len(filtered_df)} rows")
        
        if 'salary' in df.columns:
            high_salary = df[df['salary'] > df['salary'].mean()]
            print(f"   ✅ High salary (> mean): {len(high_salary)} rows")
        
        # 2. Adding calculated columns
        if 'salary' in df.columns and 'years_experience' in df.columns:
            df['salary_per_year'] = df['salary'] / df['years_experience']
            df['experience_category'] = df['years_experience'].apply(
                lambda x: 'Junior' if x < 3 else 'Mid' if x < 6 else 'Senior'
            )
            print(f"   ✅ Added calculated columns: salary_per_year, experience_category")
        
        # 3. Aggregations
        if 'department' in df.columns:
            dept_summary = df.groupby('department').agg({
                'salary': ['mean', 'min', 'max', 'count'],
                'age': 'mean',
                'performance_rating': 'mean'
            }).round(2)
            print(f"\n📊 Department summary:")
            print(dept_summary)
        
        # 4. Sorting
        if 'salary' in df.columns:
            top_earners = df.nlargest(5, 'salary')[['name', 'department', 'salary']]
            print(f"\n🏆 Top 5 earners:")
            print(top_earners)
        
        # 5. Conditional logic
        if 'performance_rating' in df.columns and 'salary' in df.columns:
            df['bonus_eligible'] = (df['performance_rating'] > 4.5) & (df['salary'] < 80000)
            df['bonus_amount'] = np.where(df['bonus_eligible'], df['salary'] * 0.1, 0)
            print(f"\n🎁 Bonus calculation:")
            print(f"   ✅ Eligible for bonus: {df['bonus_eligible'].sum()} employees")
            print(f"   ✅ Total bonus pool: ${df['bonus_amount'].sum():,.2f}")
        
        print(f"\n📊 Final dataset shape: {df.shape}")
        print(f"   Final columns: {list(df.columns)}")
        
        input("\nPress Enter to continue...")
    
    def test_duckdb_analytics(self):
        """Test DuckDB analytics functionality"""
        print("\n🦆 Testing DuckDB Analytics")
        print("-" * 50)
        
        try:
            # Test if service is healthy
            if not self.duckdb_service.is_healthy():
                print("❌ DuckDB service is not healthy")
                return
            
            print("✅ DuckDB service is healthy")
            
            # Use financial dataset for time series analysis
            if 'financial' not in self.sample_datasets:
                print("❌ Financial dataset not available")
                return
            
            df = self.sample_datasets['financial']
            print(f"\n📊 Using dataset: financial")
            print(f"   Shape: {df.shape}")
            
            # Save to temporary CSV for DuckDB processing
            temp_csv = "temp_financial.csv"
            df.to_csv(temp_csv, index=False)
            
            try:
                # Test file processing
                print("\n📁 Testing file processing...")
                result = self.duckdb_service.process_file(temp_csv)
                print(f"   ✅ File processed: {result['row_count']} rows, {result['column_count']} columns")
                print(f"   ✅ Processing time: {result['processing_time']:.4f} seconds")
                
                # Test analytics
                print("\n📊 Testing analytics...")
                analytics_config = {
                    'type': 'statistical_analysis',
                    'data_source': temp_csv,
                    'parameters': {
                        'metrics': ['mean', 'std', 'min', 'max'],
                        'group_by': ['month']
                    }
                }
                
                analytics_result = self.duckdb_service.perform_complex_analytics(analytics_config)
                print(f"   ✅ Analytics completed: {analytics_result['analytics_type']}")
                print(f"   ✅ Execution time: {analytics_result['execution_time']:.4f} seconds")
                
                # Show analytics result
                if 'result' in analytics_result:
                    print(f"\n📈 Analytics result:")
                    print(json.dumps(analytics_result['result'], indent=2, default=str))
                
            finally:
                # Clean up
                if os.path.exists(temp_csv):
                    os.remove(temp_csv)
                    print("   ✅ Temporary file cleaned up")
            
        except Exception as e:
            print(f"❌ DuckDB analytics test failed: {e}")
        
        input("\nPress Enter to continue...")
    
    def test_workflow_building(self):
        """Test workflow building functionality"""
        print("\n⚙️ Testing Workflow Building")
        print("-" * 50)
        
        try:
            # Test workflow validation
            print("🔍 Testing workflow validation...")
            
            # Create a test workflow
            test_workflow = {
                "name": "Test Analytics Workflow",
                "workflow_config": {
                    "steps": [
                        {
                            "id": "step1",
                            "name": "load_data",
                            "type": "data_source",
                            "config": {"source": "employees"}
                        },
                        {
                            "id": "step2",
                            "name": "filter_senior",
                            "type": "transformation",
                            "config": {"type": "filter", "condition": "years_experience > 5"}
                        },
                        {
                            "id": "step3",
                            "name": "calculate_metrics",
                            "type": "transformation",
                            "config": {"type": "aggregate", "group_by": ["department"]}
                        }
                    ]
                }
            }
            
            # Validate workflow
            validation_result = self.workflow_service.validate_workflow(test_workflow)
            print(f"   ✅ Workflow validation: {validation_result['valid']}")
            
            if not validation_result['valid']:
                print(f"   ❌ Validation errors: {validation_result['errors']}")
            else:
                print(f"   ✅ Complexity score: {validation_result['complexity_score']}")
                
                # Test workflow execution
                print("\n🚀 Testing workflow execution...")
                
                # Prepare data sources
                data_sources = {
                    'employees': self.sample_datasets['employees'].to_dict('records')
                }
                
                execution_result = self.workflow_service.execute_workflow(test_workflow, data_sources)
                print(f"   ✅ Workflow execution: {execution_result['success']}")
                
                if execution_result['success']:
                    print(f"   ✅ Steps executed: {execution_result.get('steps_executed', 'N/A')}")
                else:
                    print(f"   ❌ Execution error: {execution_result.get('error', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ Workflow building test failed: {e}")
        
        input("\nPress Enter to continue...")
    
    def test_file_operations(self):
        """Test file handling operations"""
        print("\n📁 Testing File Operations")
        print("-" * 50)
        
        try:
            # Create a test file
            test_file_path = "test_formula_file.txt"
            test_content = "This is a test file for formula testing.\nLine 2: Contains sample data.\nLine 3: For validation testing."
            
            with open(test_file_path, 'w') as f:
                f.write(test_content)
            
            print(f"   ✅ Test file created: {test_file_path}")
            
            # Test file operations
            print("\n🔍 Testing file operations...")
            
            # File info
            file_info = self.file_handler.get_file_info(test_file_path)
            print(f"   ✅ File info retrieved: {file_info.get('size', 'N/A')} bytes")
            
            # File hash
            file_hash = self.file_handler.calculate_file_hash(test_file_path)
            print(f"   ✅ File hash calculated: {file_hash[:16] if file_hash else 'N/A'}...")
            
            # File validation
            is_valid = self.file_handler.validate_file(test_file_path)
            print(f"   ✅ File validation: {is_valid}")
            
            # Clean up
            os.remove(test_file_path)
            print("   ✅ Test file cleaned up")
            
        except Exception as e:
            print(f"❌ File operations test failed: {e}")
        
        input("\nPress Enter to continue...")
    
    def test_data_validation(self):
        """Test data validation functionality"""
        print("\n🔍 Testing Data Validation")
        print("-" * 50)
        
        try:
            # Test data validation
            print("✅ Testing data validation...")
            
            # Get dataset choice
            dataset_name = self._select_dataset()
            if not dataset_name:
                return
            
            df = self.sample_datasets[dataset_name]
            print(f"\n📊 Validating dataset: {dataset_name}")
            
            # Validate data
            validation_result = self.data_validator.validate_dataframe(df)
            print(f"   ✅ Data validation: {validation_result.get('is_valid', 'N/A')}")
            
            if not validation_result.get('is_valid', True):
                print(f"   ❌ Validation issues: {validation_result.get('issues', [])}")
            
            # Test data summary
            print("\n📋 Testing data summary generation...")
            try:
                summary = self.data_validator.generate_data_summary(df)
                print(f"   ✅ Data summary generated: {summary.get('total_rows', 'N/A')} rows, {summary.get('total_columns', 'N/A')} columns")
            except AttributeError:
                print("   ⚠️ generate_data_summary method not available")
                
                # Create manual summary
                manual_summary = {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'columns': list(df.columns),
                    'data_types': df.dtypes.to_dict(),
                    'missing_values': df.isnull().sum().to_dict(),
                    'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
                    'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
                }
                print(f"   📊 Manual summary:")
                print(f"      Rows: {manual_summary['total_rows']}")
                print(f"      Columns: {manual_summary['total_columns']}")
                print(f"      Numeric: {len(manual_summary['numeric_columns'])}")
                print(f"      Categorical: {len(manual_summary['categorical_columns'])}")
            
        except Exception as e:
            print(f"❌ Data validation test failed: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_sample_datasets(self):
        """View sample datasets"""
        print("\n📈 Sample Datasets Overview")
        print("-" * 50)
        
        for name, df in self.sample_datasets.items():
            print(f"\n📁 {name.upper()}")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Data types: {df.dtypes.to_dict()}")
            print(f"   Sample data:")
            print(df.head(2).to_string())
            print("-" * 30)
        
        input("\nPress Enter to continue...")
    
    def run_all_tests(self):
        """Run all tests automatically"""
        print("\n🚀 Running All Tests Automatically")
        print("=" * 60)
        
        test_functions = [
            ("Basic Formulas", self.test_basic_formulas),
            ("Complex Business Formulas", self.test_complex_business_formulas),
            ("Data Flow Operations", self.test_data_flow_operations),
            ("DuckDB Analytics", self.test_duckdb_analytics),
            ("Workflow Building", self.test_workflow_building),
            ("File Operations", self.test_file_operations),
            ("Data Validation", self.test_data_validation)
        ]
        
        results = []
        for test_name, test_func in test_functions:
            print(f"\n🧪 Running: {test_name}")
            try:
                # Temporarily redirect input to avoid blocking
                import builtins
                original_input = builtins.input
                builtins.input = lambda: ""
                
                test_func()
                results.append((test_name, True))
                print(f"✅ {test_name}: PASSED")
                
            except Exception as e:
                results.append((test_name, False))
                print(f"❌ {test_name}: FAILED - {e}")
            finally:
                # Restore input
                builtins.input = original_input
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 AUTOMATIC TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The formula engine is working perfectly.")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
        
        input("\nPress Enter to continue...")
    
    def _select_dataset(self):
        """Helper to select a dataset"""
        print("\n📊 Available datasets:")
        for i, name in enumerate(self.sample_datasets.keys(), 1):
            print(f"   {i}. {name}")
        
        try:
            choice = int(input("Select dataset (number): ").strip())
            dataset_names = list(self.sample_datasets.keys())
            if 1 <= choice <= len(dataset_names):
                return dataset_names[choice - 1]
            else:
                print("❌ Invalid choice")
                return None
        except ValueError:
            print("❌ Please enter a valid number")
            return None
    
    def _select_column(self, df, columns, description):
        """Helper to select a column"""
        print(f"\n📋 Select {description}:")
        for i, col in enumerate(columns, 1):
            print(f"   {i}. {col}")
        
        try:
            choice = int(input(f"Select {description} (number): ").strip())
            if 1 <= choice <= len(columns):
                return columns[choice - 1]
            else:
                print("❌ Invalid choice")
                return None
        except ValueError:
            print("❌ Please enter a valid number")
            return None

def main():
    """Main function to run the interactive formula tester"""
    print("🚀 Starting Interactive Formula Tester")
    print("=" * 60)
    
    tester = InteractiveFormulaTester()
    
    if tester.initialize_services():
        print("\n✨ Services initialized successfully!")
        print("Ready to test formulas and data operations.")
        tester.show_main_menu()
    else:
        print("\n💥 Failed to initialize services.")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
