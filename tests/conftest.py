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
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()

@pytest.fixture(scope="function")
def db_tx(db_conn):
    prev = db_conn.get_autocommit()
    if prev:
        db_conn.autocommit(False)
    try:
        yield db_conn
        db_conn.rollback()  # ensure clean DB
    finally:
        if prev:
            db_conn.autocommit(True)
