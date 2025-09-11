from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Optional, Sequence

import MySQLdb
import MySQLdb.cursors

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

def connect(autocommit: bool = True) -> MySQLdb.connections.Connection:
    cfg = config_from_env()
    conn = MySQLdb.connect(
        host = cfg.host,
        port = cfg.port,
        user = cfg.user,
        passwd = cfg.passwd,
        db = cfg.db,
        charset = cfg.charset,
        use_unicode = cfg.use_unicode,
    )
    conn.autocommit(autocommit)
    return conn

def dict_cursor(conn: MySQLdb.connections.Connection) -> MySQLdb.cursors.Cursor:
    return conn.cursor(MySQLdb.cursors.DictCursor)

@contextmanager
def db_conn(autocommit: bool = True):
    conn = connect(autocommit=autocommit)
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass

@contextmanager
def db_cursor(conn: MySQLdb.connections.Connection, dict_rows: bool = True):
    cur = conn.cursor(MySQLdb.cursors.DictCursor if dict_rows else None)
    try:
        yield cur
    finally:
        try:
            cur.close()
        except Exception:
            pass

@contextmanager
def transaction(conn: MySQLdb.connections.Connection):
    prev = conn.get_autocommit()
    if prev:
        conn.autocommit(False)
    try:
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if prev:
            conn.autocommit(True)

def execute(cur: MySQLdb.cursors.Cursor, sql: str, params: Optional[Sequence[Any]] = None) -> int:
    return cur.execute(sql, params or ())

def fetch_one(conn: MySQLdb.connections.Connection, sql: str, params: Optional[Sequence[Any]] = None) -> Optional[dict]:
    with db_cursor(conn) as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()
    
def fetch_all(conn: MySQLdb.connections.Connection, sql: str, params: Optional[Sequence[Any]] = None) ->list[dict]:
    with db_cursor(conn) as cur:
        cur.execute(sql, params or ())
        return list(cur.fetchall())
    
def insert_one(
        conn: MySQLdb.connections.Connection,
        table: str,
        columns: Sequence[str],
        values: Sequence[Any],
        update_cols: Sequence[str],
) -> int:
    placeholders = ", ".join(["%s"]*len(columns))
    cols = ", ".join(f"{c}" for c in columns)
    update_expr = ", ".join(f"{c} = new.{c}" for c in update_cols)
    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) AS new ON DUPLICATE KEY UPDATE {update_expr}"
    with db_cursor(conn, dict_rows=False) as cur:
        return cur.execute(sql, tuple(values))
    
def ping() -> bool:
    try:
        with db_conn() as conn:
            with db_cursor(conn) as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False