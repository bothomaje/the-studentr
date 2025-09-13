from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Optional, Sequence

from PyQt5.QtSql import QSqlDatabase, QSqlQuery

class NotFoundError(RuntimeError):
    pass

class ForbiddenError(RuntimeError):
    pass

@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    user: str
    passwd: str
    db: str
    charset: str = "utf8mb4"
    use_unicode: bool = True

def _load_env_into_os():
    try:
        from app.config.env import load_env
    except Exception:
        return False
    return load_env()

def config_from_env() -> DBConfig:
    _load_env_into_os()
    return DBConfig(
        host = os.getenv("SA_DB_HOST", "localhost"),
        port = int(os.getenv("SA_DB_PORT", "3306")),
        user = os.getenv("SA_DB_USER", "root"),
        passwd = os.getenv("SA_DB_PASS", ""),
        db = os.getenv("SA_DB_NAME", "the_studentr"),
    )

def connect(autocommit: bool = True) -> QSqlDatabase:
    cfg = config_from_env()
    
    # Generate a unique connection name for this thread/connection
    connection_name = f"mysql_conn_{id(cfg)}"
    
    # Remove any existing connection with this name
    if QSqlDatabase.contains(connection_name):
        QSqlDatabase.removeDatabase(connection_name)
    
    # Use MySQL driver (simplified for MySQL-only deployment)
    available_drivers = QSqlDatabase.drivers()
    
    if "QMYSQL" in available_drivers or "QMYSQL3" in available_drivers:
        # Use native MySQL driver
        driver_name = "QMYSQL" if "QMYSQL" in available_drivers else "QMYSQL3"
        db = QSqlDatabase.addDatabase(driver_name, connection_name)
        db.setHostName(cfg.host)
        db.setPort(cfg.port)
        db.setUserName(cfg.user)
        db.setPassword(cfg.passwd)
        db.setDatabaseName(cfg.db)
        # Connection configured (charset defaults to UTF-8 in modern MySQL)
    else:
        raise RuntimeError(
            "MySQL driver not available. Please install the Qt5 MySQL driver.\n"
            "Ubuntu/Debian: sudo apt-get install libqt5sql5-mysql python3-pyqt5\n"
            "CentOS/RHEL: sudo yum install qt5-qtbase-mysql\n"
            "macOS: brew install qt@5\n"
            "Windows: Install Qt5 with MySQL support\n"
            f"Available drivers: {available_drivers}"
        )
    
    if not db.open():
        error = db.lastError()
        error_msg = f"Failed to connect to database: {error.text()}"
        
        # Provide helpful error messages for common issues
        if "Can't open lib" in error.text() and "MySQL ODBC" in error.text():
            error_msg += (
                "\n\nThis error indicates that the native MySQL Qt driver is not installed.\n"
                "Please install it using:\n"
                "Ubuntu/Debian: sudo apt-get install libqt5sql5-mysql\n"
                "CentOS/RHEL: sudo yum install qt5-qtbase-mysql\n"
                "macOS: brew install qt@5\n"
                "Windows: Install Qt5 with MySQL support"
            )
        elif "Access denied" in error.text():
            error_msg += (
                "\n\nThis error indicates incorrect database credentials.\n"
                "Please check your .env file settings:\n"
                f"SA_DB_HOST={cfg.host}\n"
                f"SA_DB_PORT={cfg.port}\n"
                f"SA_DB_USER={cfg.user}\n"
                "SA_DB_PASS=<your_password>"
            )
        
        raise RuntimeError(error_msg)
    
    # Set autocommit mode (for MySQL)
    query = QSqlQuery(db)
    if autocommit:
        if not query.exec_("SET autocommit = 1"):
            pass
    else:
        if not query.exec_("SET autocommit = 0"):
            pass
    
    return db

def create_query(db: QSqlDatabase) -> QSqlQuery:
    return QSqlQuery(db)

@contextmanager
def db_conn(autocommit: bool = True):
    db = connect(autocommit=autocommit)
    try:
        yield db
    finally:
        try:
            connection_name = db.connectionName()
            db.close()
            QSqlDatabase.removeDatabase(connection_name)
        except Exception:
            pass

@contextmanager
def db_query(db: QSqlDatabase):
    query = QSqlQuery(db)
    try:
        yield query
    finally:
        try:
            query.finish()
        except Exception:
            pass

@contextmanager
def transaction(db: QSqlDatabase):
    # Check if we're already in a transaction
    was_autocommit = True
    query = QSqlQuery(db)
    query.exec_("SELECT @@autocommit")
    if query.next():
        was_autocommit = query.value(0) == 1
    
    if was_autocommit:
        if not db.transaction():
            raise RuntimeError(f"Failed to start transaction: {db.lastError().text()}")
    
    try:
        yield
        if was_autocommit:
            if not db.commit():
                raise RuntimeError(f"Failed to commit transaction: {db.lastError().text()}")
    except Exception:
        if was_autocommit:
            if not db.rollback():
                print(f"Warning: Failed to rollback transaction: {db.lastError().text()}")
        raise

def execute(query: QSqlQuery, sql: str, params: Optional[Sequence[Any]] = None) -> int:
    """Execute a SQL query and return the number of affected rows."""
    if params:
        # Prepare the query with placeholders
        if not query.prepare(sql):
            _check_sql_error(query)
            raise RuntimeError(f"Failed to prepare query: {query.lastError().text()}")
        
        # Bind parameters
        for param in params:
            query.addBindValue(param)
        
        # Execute the prepared query
        if not query.exec_():
            _check_sql_error(query)
            raise RuntimeError(f"Failed to execute query: {query.lastError().text()}")
    else:
        # Execute directly without parameters
        if not query.exec_(sql):
            _check_sql_error(query)
            raise RuntimeError(f"Failed to execute query: {query.lastError().text()}")
    
    return query.numRowsAffected()

def _query_to_dict(query: QSqlQuery) -> dict:
    """Convert a QSqlQuery result record to a dictionary."""
    record = query.record()
    result = {}
    for i in range(record.count()):
        field_name = record.fieldName(i)
        value = query.value(i)
        result[field_name] = value
    return result

def fetch_one(db: QSqlDatabase, sql: str, params: Optional[Sequence[Any]] = None) -> Optional[dict]:
    with db_query(db) as query:
        execute(query, sql, params)
        if query.next():
            return _query_to_dict(query)
        return None
    
def fetch_all(db: QSqlDatabase, sql: str, params: Optional[Sequence[Any]] = None) -> list[dict]:
    with db_query(db) as query:
        execute(query, sql, params)
        results = []
        while query.next():
            results.append(_query_to_dict(query))
        return results
    
def insert_one(
        db: QSqlDatabase,
        table: str,
        columns: Sequence[str],
        values: Sequence[Any],
        update_cols: Sequence[str],
) -> int:
    placeholders = ", ".join(["?"]*len(columns))
    cols = ", ".join(f"{c}" for c in columns)
    update_expr = ", ".join(f"{c} = new.{c}" for c in update_cols)
    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) AS new ON DUPLICATE KEY UPDATE {update_expr}"
    with db_query(db) as query:
        return execute(query, sql, tuple(values))
    
def ping() -> bool:
    try:
        with db_conn() as db:
            with db_query(db) as query:
                execute(query, "SELECT 1")
                query.next()
        return True
    except Exception:
        return False

# Custom exception classes to match MySQLdb behavior
class DatabaseError(Exception):
    """Base exception for database errors."""
    def __init__(self, message: str, error_code: int = 0):
        super().__init__(message)
        self.args = (error_code, message)

class IntegrityError(DatabaseError):
    """Exception for database integrity constraint violations."""
    pass

def _check_sql_error(query: QSqlQuery):
    """Check for SQL errors and raise appropriate exceptions."""
    if query.lastError().isValid():
        error = query.lastError()
        error_text = error.text()
        error_code = error.number()
        
        # Map common MySQL error codes to appropriate exceptions
        integrity_error_codes = {1048, 1062, 1216, 1217, 1451, 1452}  # NOT NULL, DUPLICATE, FK constraints
        
        if error_code in integrity_error_codes:
            raise IntegrityError(error_text, error_code)
        else:
            raise DatabaseError(error_text, error_code)
