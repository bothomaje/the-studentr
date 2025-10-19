import pytest
from app.dal.base import connect

# Define pytest markers for test categorization
def pytest_configure(config):
    config.addinivalue_line("markers", "database: marks tests that require database connectivity")
    config.addinivalue_line("markers", "dal: marks tests for Data Access Layer functionality")
    config.addinivalue_line("markers", "ui: marks tests for User Interface components")
    config.addinivalue_line("markers", "integration: marks tests that test component integration")

@pytest.fixture(scope="function")
def db_conn():
    db = connect()
    try:
        yield db
    finally:
        connection_name = db.connectionName()
        db.close()
        from PyQt5.QtSql import QSqlDatabase
        QSqlDatabase.removeDatabase(connection_name)

@pytest.fixture(scope="function")
def db_tx(db_conn):
    # Start a transaction
    if not db_conn.transaction():
        raise RuntimeError(f"Failed to start transaction: {db_conn.lastError().text()}")
    try:
        yield db_conn
        # Always rollback to ensure clean DB
        if not db_conn.rollback():
            print(f"Warning: Failed to rollback transaction: {db_conn.lastError().text()}")
    except Exception:
        if not db_conn.rollback():
            print(f"Warning: Failed to rollback transaction: {db_conn.lastError().text()}")
        raise
