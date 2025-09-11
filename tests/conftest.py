import pytest
from app.dal.base import connect

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
