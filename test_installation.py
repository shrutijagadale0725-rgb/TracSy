#!/usr/bin/env python3
"""
test_installation.py
Quick test script to verify all dependencies and modules are working.
Run this before running the main application.
"""

import sys

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing package imports...\n")
    
    packages = {
        'streamlit': 'Streamlit UI framework',
        'sqlalchemy': 'SQLAlchemy ORM',
        'pandas': 'Pandas data processing',
        'matplotlib': 'Matplotlib visualization',
        'PyPDF2': 'PyPDF2 PDF parsing'
    }
    
    failed = []
    
    for package, description in packages.items():
        try:
            if package == 'PyPDF2':
                __import__('PyPDF2')
            else:
                __import__(package)
            print(f"✅ {package:15} - {description}")
        except ImportError as e:
            print(f"❌ {package:15} - FAILED: {e}")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("Please run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True


def test_modules():
    """Test if all custom modules can be imported."""
    print("\nTesting custom modules...\n")
    
    modules = {
        'database': 'Database models and setup',
        'auth': 'Authentication logic',
        'crud': 'CRUD operations',
        'charts': 'Visualization functions',
        'file_parser': 'CSV/PDF parsing'
    }
    
    failed = []
    
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"✅ {module:15} - {description}")
        except Exception as e:
            print(f"❌ {module:15} - FAILED: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("Make sure all .py files are in the same directory!")
        return False
    else:
        print("\n✅ All custom modules imported successfully!")
        return True


def test_database():
    """Test database creation."""
    print("\nTesting database setup...\n")
    
    try:
        from database import init_db, Base, engine
        import os
        
        # Initialize database
        init_db()
        
        # Check if database file created
        if os.path.exists('finance.db'):
            print("✅ Database file created successfully!")
            
            # Check tables
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'users' in tables and 'transactions' in tables:
                print("✅ Database tables created successfully!")
                print(f"   Tables: {', '.join(tables)}")
                return True
            else:
                print("❌ Database tables not created properly!")
                return False
        else:
            print("❌ Database file not created!")
            return False
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def test_file_parser():
    """Test CSV parsing functionality."""
    print("\nTesting CSV parser...\n")
    
    try:
        from file_parser import parse_csv
        import pandas as pd
        from io import StringIO
        
        # Create test CSV
        test_csv = StringIO("""date,amount,description
2024-01-15,5000,Test Transaction
2024-01-16,250,Another Test""")
        
        df = parse_csv(test_csv)
        
        if df is not None and len(df) == 2:
            print("✅ CSV parser working correctly!")
            print(f"   Parsed {len(df)} rows successfully")
            return True
        else:
            print("❌ CSV parser not working correctly!")
            return False
            
    except Exception as e:
        print(f"❌ CSV parser test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Personal Budget Monitoring System - Installation Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Package imports
    results.append(test_imports())
    
    # Test 2: Custom modules
    results.append(test_modules())
    
    # Test 3: Database setup
    results.append(test_database())
    
    # Test 4: File parser
    results.append(test_file_parser())
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("\nYour system is ready to run.")
        print("Start the application with: streamlit run main.py")
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nPlease fix the issues above before running the application.")
        print("Common fixes:")
        print("  1. Install packages: pip install -r requirements.txt")
        print("  2. Make sure all .py files are present")
        print("  3. Run from the correct directory")
    
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)