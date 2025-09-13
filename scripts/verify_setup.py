#!/usr/bin/env python3
"""
Database connection verification script for the-studentr application.

This script helps verify that the database setup is working correctly
after the migration to PyQt QSql module.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PyQt5.QtSql import QSqlDatabase, QSqlQuery
    from app.config.env import load_env
    from app.dal.base import db_conn, ping
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure PyQt5 is installed: pip install PyQt5==5.15.10")
    sys.exit(1)

def check_drivers():
    """Check what SQL drivers are available."""
    print("=== SQL Driver Check ===")
    available_drivers = QSqlDatabase.drivers()
    print(f"Available drivers: {available_drivers}")
    
    # Check for MySQL support
    mysql_drivers = [d for d in available_drivers if 'MYSQL' in d.upper()]
    
    if mysql_drivers:
        print(f"✅ MySQL drivers: {mysql_drivers}")
        return True
    else:
        print("❌ No MySQL drivers found")
        print("   Please install Qt5 MySQL driver:")
        print("   Ubuntu/Debian: sudo apt-get install libqt5sql5-mysql python3-pyqt5")
        return False

def check_environment():
    """Check environment configuration."""
    print("\n=== Environment Check ===")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
        if Path(".env.example").exists():
            print("   Copy .env.example to .env and configure it")
        return False
    
    # Load environment
    if load_env():
        print("✅ Environment loaded successfully")
    else:
        print("❌ Failed to load environment")
        return False
    
    # Check required variables
    required_vars = ["SA_DB_HOST", "SA_DB_PORT", "SA_DB_USER", "SA_DB_NAME"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == "SA_DB_PASS":
                print(f"✅ {var}: [hidden]")
            else:
                print(f"✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: not set")
    
    if missing_vars:
        print(f"Missing required variables: {missing_vars}")
        return False
    
    return True

def test_connection():
    """Test database connection."""
    print("\n=== Connection Test ===")
    
    try:
        if ping():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database ping failed")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_basic_query():
    """Test basic database operations."""
    print("\n=== Basic Query Test ===")
    
    try:
        with db_conn() as db:
            query = QSqlQuery(db)
            
            # Test a simple query
            if query.exec_("SELECT 1 as test"):
                if query.next():
                    result = query.value(0)
                    print(f"✅ Basic query successful: {result}")
                    return True
                else:
                    print("❌ Query executed but no results")
                    return False
            else:
                error = query.lastError()
                print(f"❌ Query failed: {error.text()}")
                return False
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def test_tables():
    """Test if required tables exist."""
    print("\n=== Table Check ===")
    
    try:
        with db_conn() as db:
            query = QSqlQuery(db)
            
            # Check for tables (MySQL only)
            if query.exec_("SELECT table_name as name FROM information_schema.tables WHERE table_schema = DATABASE()"):
                tables = []
                while query.next():
                    tables.append(query.value(0))
                
                required_tables = ["users", "modules", "assignments", "marks"]
                found_tables = []
                missing_tables = []
                
                for table in required_tables:
                    if table in tables:
                        found_tables.append(table)
                        print(f"✅ Table '{table}' exists")
                    else:
                        missing_tables.append(table)
                        print(f"❌ Table '{table}' missing")
                
                if missing_tables:
                    print(f"\nMissing tables: {missing_tables}")
                    print("Run: PYTHONPATH=. python scripts/setup_db.py")
                    return False
                else:
                    print("✅ All required tables found")
                    return True
            else:
                error = query.lastError()
                print(f"❌ Failed to check tables: {error.text()}")
                return False
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        return False

def main():
    """Main verification function."""
    print("🔍 Database Setup Verification")
    print("=" * 40)
    
    # Change to script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    all_checks_passed = True
    
    # Run checks
    if not check_drivers():
        all_checks_passed = False
    
    if not check_environment():
        all_checks_passed = False
    
    if not test_connection():
        all_checks_passed = False
        # If connection fails, skip other tests
        print("\n" + "=" * 40)
        print("💡 Suggestion: Install Qt5 MySQL drivers")
        print("   Ubuntu/Debian: sudo apt-get install libqt5sql5-mysql python3-pyqt5")
        print("   See DRIVER_SETUP.md for detailed instructions")
        return
    
    if not test_basic_query():
        all_checks_passed = False
    
    if not test_tables():
        all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 40)
    if all_checks_passed:
        print("🎉 All checks passed! Database setup is working correctly.")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        print("   See DRIVER_SETUP.md for troubleshooting guide.")

if __name__ == "__main__":
    main()