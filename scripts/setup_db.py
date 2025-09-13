import os
import sys
from pathlib import Path
from app.config.env import load_env
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

# Runs statements saved in sql file
def run_sql_file(query: QSqlQuery, path: Path):
    sql_text = path.read_text(encoding="utf-8")

    for statement in (s.strip() for s in sql_text.split(";")):
        if statement:
            if not query.exec_(statement):
                error = query.lastError()
                code = error.number()
                known = {1007, 1050, 1061}
                if code in known:
                    print(f"[idempotent-ok] {code} on: {statement[:120]!r}")
                else:
                    raise RuntimeError(f"SQL Error {code}: {error.text()}")

def print_driver_diagnostics():
    """Print detailed information about available SQL drivers and installation instructions."""
    available_drivers = QSqlDatabase.drivers()
    print("=== Database Driver Diagnostics ===")
    print(f"Available Qt SQL drivers: {available_drivers}")
    
    # Check for MySQL drivers
    mysql_drivers = [d for d in available_drivers if 'MYSQL' in d.upper()]
    if mysql_drivers:
        print(f"✓ MySQL drivers found: {mysql_drivers}")
        return True
    else:
        print("✗ No MySQL drivers found")
        
    # Check for ODBC drivers
    odbc_drivers = [d for d in available_drivers if 'ODBC' in d.upper()]
    if odbc_drivers:
        print(f"✓ ODBC drivers found: {odbc_drivers}")
        print("  However, MySQL ODBC driver may not be installed on the system.")
        
    print("\n=== Installation Instructions ===")
    print("To use MySQL with this application, you need one of the following:")
    print("\n1. Native MySQL driver (recommended):")
    print("   Ubuntu/Debian: sudo apt-get install libqt5sql5-mysql")
    print("   CentOS/RHEL:   sudo yum install qt5-qtbase-mysql")
    print("   macOS:         brew install qt@5 --with-mysql")
    print("   Windows:       Install Qt5 with MySQL support")
    
    print("\n2. MySQL ODBC driver (alternative):")
    print("   Ubuntu/Debian: sudo apt-get install libmyodbc")
    print("   CentOS/RHEL:   sudo yum install mysql-connector-odbc")
    print("   macOS:         brew install mysql-connector-odbc")
    print("   Windows:       Download from MySQL website")
    
    print("\n3. Development/Testing mode:")
    print("   Run with --sqlite flag to use SQLite for testing")
    print("   Note: This won't work with the full schema but allows basic testing")
    
    return False

def setup_sqlite_for_testing():
    """Set up a basic SQLite database for testing purposes."""
    print("\n=== Setting up SQLite for testing ===")
    print("Warning: This is a simplified setup for testing only.")
    print("Some features may not work as expected with SQLite.")
    
    # Create a simple SQLite connection
    db = QSqlDatabase.addDatabase("QSQLITE", "sqlite_setup")
    db.setDatabaseName("test_studentr.db")
    
    if not db.open():
        error = db.lastError()
        raise RuntimeError(f"Failed to connect to SQLite database: {error.text()}")
    
    query = QSqlQuery(db)
    
    # Create basic tables for testing (simplified schema)
    test_schema = """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        first_name TEXT,
        surname TEXT,
        password_hash TEXT
    );
    
    CREATE TABLE IF NOT EXISTS modules (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        module_code TEXT,
        module_name TEXT,
        year_mark_weight REAL,
        exam_weight REAL,
        min_assignments INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """
    
    for statement in (s.strip() for s in test_schema.split(";")):
        if statement:
            if not query.exec_(statement):
                error = query.lastError()
                print(f"SQLite setup warning: {error.text()}")
    
    # Test the setup
    if not query.exec_("SELECT name FROM sqlite_master WHERE type='table'"):
        raise RuntimeError(f"Failed to query SQLite tables: {query.lastError().text()}")
    
    tables = []
    while query.next():
        tables.append(query.value(0))
    
    print(f"SQLite tables created: {tables}")
    
    connection_name = db.connectionName()
    db.close()
    QSqlDatabase.removeDatabase(connection_name)
    
    print("SQLite setup completed successfully.")
    print(f"Database file: {os.path.abspath('test_studentr.db')}")
    return True

# setup db main function
def main():
    # Check for command line arguments
    use_sqlite = "--sqlite" in sys.argv
    show_help = "--help" in sys.argv or "-h" in sys.argv
    
    if show_help:
        print("Usage: python setup_db.py [--sqlite] [--help]")
        print("  --sqlite    Use SQLite for testing instead of MySQL")
        print("  --help      Show this help message")
        return
    
    if use_sqlite:
        setup_sqlite_for_testing()
        return
        
    # load variables and pull connection info
    load_env()
    host = os.getenv("SA_DB_HOST", "localhost")
    port = int(os.getenv("SA_DB_PORT", "3306"))
    user = os.getenv("SA_DB_USER", "root")
    passwd = os.getenv("SA_DB_PASS", "")
    dbname = os.getenv("SA_DB_NAME", "the_studentr")

    # Check available drivers first
    available_drivers = QSqlDatabase.drivers()
    print(f"Available SQL drivers: {available_drivers}")
    
    # Try to connect to MySQL
    connection_successful = False
    
    if "QMYSQL" in available_drivers or "QMYSQL3" in available_drivers:
        # Use native MySQL driver if available
        driver_name = "QMYSQL" if "QMYSQL" in available_drivers else "QMYSQL3"
        print(f"Attempting connection with {driver_name} driver...")
        
        db = QSqlDatabase.addDatabase(driver_name, "setup_connection")
        db.setHostName(host)
        db.setPort(port)
        db.setUserName(user)
        db.setPassword(passwd)
        db.setDatabaseName(dbname)
        db.setConnectOptions("MYSQL_OPT_CHARSET=utf8mb4")
        
        if db.open():
            connection_successful = True
            print(f"✓ Connected successfully using {driver_name}")
        else:
            error = db.lastError()
            print(f"✗ Failed to connect with {driver_name}: {error.text()}")
            
    elif "QODBC" in available_drivers or "QODBC3" in available_drivers:
        # Use ODBC driver as fallback
        driver_name = "QODBC" if "QODBC" in available_drivers else "QODBC3"
        print(f"Attempting connection with {driver_name} driver...")
        
        db = QSqlDatabase.addDatabase(driver_name, "setup_connection")
        # Build ODBC connection string for MySQL
        odbc_string = (f"DRIVER={{MySQL ODBC 8.0 Unicode Driver}};"
                      f"SERVER={host};"
                      f"PORT={port};"
                      f"DATABASE={dbname};"
                      f"UID={user};"
                      f"PWD={passwd};"
                      f"CHARSET=utf8mb4;")
        db.setDatabaseName(odbc_string)
        
        if db.open():
            connection_successful = True
            print(f"✓ Connected successfully using {driver_name}")
        else:
            error = db.lastError()
            print(f"✗ Failed to connect with {driver_name}: {error.text()}")
    
    if not connection_successful:
        print("\n" + "="*50)
        print("DATABASE CONNECTION FAILED")
        print("="*50)
        print_driver_diagnostics()
        print("\nPlease install the required MySQL drivers or use --sqlite for testing.")
        sys.exit(1)
    
    # Continue with setup if connection was successful
    
    query = QSqlQuery(db)
    schema = Path("db/schema.sql")
    seed = Path("db/seed.sql")

    # apply schema.sql
    if schema.exists():
        if not db.transaction():
            raise RuntimeError(f"Failed to start transaction: {db.lastError().text()}")
        try:
            run_sql_file(query, schema)
            if not db.commit():
                raise RuntimeError(f"Failed to commit transaction: {db.lastError().text()}")
        except:
            if not db.rollback():
                print(f"Warning: Failed to rollback transaction: {db.lastError().text()}")
            raise

    # apply seed.sql
    if seed.exists():
        if not db.transaction():
            raise RuntimeError(f"Failed to start transaction: {db.lastError().text()}")
        try:
            run_sql_file(query, seed)
            if not db.commit():
                raise RuntimeError(f"Failed to commit transaction: {db.lastError().text()}")
        except:
            if not db.rollback():
                print(f"Warning: Failed to rollback transaction: {db.lastError().text()}")
            raise

    # sanity check - print tables
    if not query.exec_("SHOW TABLES"):
        raise RuntimeError(f"Failed to execute SHOW TABLES: {query.lastError().text()}")
    
    tables = []
    while query.next():
        tables.append(query.value(0))
    
    print("Tables: ", ", ".join(tables))
    for t in ("users", "modules", "assignments", "marks"):
        if t in tables:
            if not query.exec_(f"SELECT COUNT(*) FROM {t}"):
                raise RuntimeError(f"Failed to count {t}: {query.lastError().text()}")
            if query.next():
                print(f"{t}: {query.value(0)}")

    connection_name = db.connectionName()
    db.close()
    QSqlDatabase.removeDatabase(connection_name)
    print(dbname, " has been set up successfully.")

# run main
if __name__ == "__main__":
    main()