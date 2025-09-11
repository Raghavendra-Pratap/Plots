#!/usr/bin/env python3
"""
Test script for Unified Data Studio
Verifies that the application can start without errors
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test backend imports
        from backend.services.duckdb_service import DuckDBService
        print("✓ DuckDBService imported successfully")
        
        from backend.services.data_service import DataService
        print("✓ DataService imported successfully")
        
        from backend.services.workflow_service import WorkflowService
        print("✓ WorkflowService imported successfully")
        
        from backend.models.database import init_database
        print("✓ Database module imported successfully")
        
        from backend.utils.file_handler import FileHandler
        print("✓ FileHandler imported successfully")
        
        from backend.utils.data_validator import DataValidator
        print("✓ DataValidator imported successfully")
        
        # Test frontend imports
        from frontend.components.main_window import MainWindow
        print("✓ MainWindow imported successfully")
        
        from frontend.components.playground import Playground
        print("✓ Playground imported successfully")
        
        from frontend.components.projects import Projects
        print("✓ Projects imported successfully")
        
        from frontend.components.workflows import Workflows
        print("✓ Workflows imported successfully")
        
        from frontend.components.analytics import Analytics
        print("✓ Analytics imported successfully")
        
        from frontend.components.settings import Settings
        print("✓ Settings imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

def test_backend_services():
    """Test that backend services can be initialized"""
    print("\nTesting backend services...")
    
    try:
        # Test DuckDB service
        duckdb_service = DuckDBService()
        print("✓ DuckDB service initialized")
        
        # Test Data service
        data_service = DataService()
        print("✓ Data service initialized")
        
        # Test Workflow service
        workflow_service = WorkflowService()
        print("✓ Workflow service initialized")
        
        # Test File handler
        file_handler = FileHandler()
        print("✓ File handler initialized")
        
        # Test Data validator
        data_validator = DataValidator()
        print("✓ Data validator initialized")
        
        print("✅ All backend services initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Backend service initialization failed: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    
    try:
        # Initialize database
        success = init_database()
        if success:
            print("✅ Database initialized successfully!")
            return True
        else:
            print("❌ Database initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Unified Data Studio - Python PySide6 Version")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your installation.")
        return False
    
    # Test backend services
    if not test_backend_services():
        print("\n❌ Backend service tests failed.")
        return False
    
    # Test database
    if not test_database():
        print("\n❌ Database tests failed.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The application is ready to run.")
    print("\nTo start the application, run:")
    print("  python main.py")
    print("\nOr install and run:")
    print("  pip install -e .")
    print("  unified-data-studio")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
