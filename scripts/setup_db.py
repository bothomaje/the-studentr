import os
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

# setup db main function
def main():
    # load variables and pull connection info
    load_env()
    host = os.getenv("SA_DB_HOST", "localhost")
    port = int(os.getenv("SA_DB_PORT", "3306"))
    user = os.getenv("SA_DB_USER", "root")
    passwd = os.getenv("SA_DB_PASS", "")
    dbname = os.getenv("SA_DB_NAME", "the_studentr")

    # connect to db
    available_drivers = QSqlDatabase.drivers()
    
    if "QMYSQL" in available_drivers or "QMYSQL3" in available_drivers:
        # Use native MySQL driver if available
        driver_name = "QMYSQL" if "QMYSQL" in available_drivers else "QMYSQL3"
        db = QSqlDatabase.addDatabase(driver_name, "setup_connection")
        db.setHostName(host)
        db.setPort(port)
        db.setUserName(user)
        db.setPassword(passwd)
        db.setConnectOptions("MYSQL_OPT_CHARSET=utf8mb4")
    elif "QODBC" in available_drivers or "QODBC3" in available_drivers:
        # Use ODBC driver as fallback
        driver_name = "QODBC" if "QODBC" in available_drivers else "QODBC3"
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
    else:
        print("Warning: No MySQL drivers available. Setup script requires MySQL connectivity.")
        print("Available drivers:", available_drivers)
        return
    
    if not db.open():
        error = db.lastError()
        raise RuntimeError(f"Failed to connect to database: {error.text()}")
    
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