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
        
    print("\n=== Installation Instructions ===")
    print("To use MySQL with this application, install the Qt5 MySQL driver:")
    print("   Ubuntu/Debian: sudo apt-get install libqt5sql5-mysql python3-pyqt5")
    print("   CentOS/RHEL:   sudo yum install qt5-qtbase-mysql")
    print("   macOS:         brew install qt@5")
    print("   Windows:       Install Qt5 with MySQL support")
    
    return False


# setup db main function
def main():
    # Check for command line arguments
    show_help = "--help" in sys.argv or "-h" in sys.argv
    
    if show_help:
        print("Usage: python setup_db.py [--help]")
        print("  --help      Show this help message")
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
        # Use native MySQL driver
        driver_name = "QMYSQL" if "QMYSQL" in available_drivers else "QMYSQL3"
        print(f"Attempting connection with {driver_name} driver...")
        
        db = QSqlDatabase.addDatabase(driver_name, "setup_connection")
        db.setHostName(host)
        db.setPort(port)
        db.setUserName(user)
        db.setPassword(passwd)
        db.setDatabaseName(dbname)
        # Connection configured (charset defaults to UTF-8 in modern MySQL)
        
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
        print("\nPlease install the required MySQL drivers.")
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
        table_name = query.value(0)
        # Convert QByteArray to string if necessary (for system Qt compatibility)
        if hasattr(table_name, 'data'):
            table_name = table_name.data().decode('utf-8')
        tables.append(str(table_name))
    
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