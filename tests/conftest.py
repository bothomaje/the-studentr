import uuid
import pytest
from app.dal.base import connect, transaction

@pytest.fixture(scope="function")
def db_conn():
    conn = connect()
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass

@pytest.fixture(scope="function")
def db_tx(db_conn):
    with transaction(db_conn) as cur:
        yield cur
        raise pytest.skip.Exception("ROLLBACK")
