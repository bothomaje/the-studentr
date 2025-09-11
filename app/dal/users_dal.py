from __future__ import annotations

import uuid
from typing import Optional

import MySQLdb

from app.dal.base import db_conn, db_cursor, fetch_one, execute, transaction

try:
    import bcrypt
except Exception:
    bcrypt = None

class UserAlreadyExists(Exception):
    pass

def _require_bcrypt():
    if bcrypt is None:
        raise RuntimeError("Missing dependency (bcrypt)")
    
def hash_password(plain: str, rounds: int = 12) -> str:
    _require_bcrypt()
    if plain is None:
        plain = ""
    salt = bcrypt.gensalt(rounds)
    hashed = bcrypt.hashpw(plain.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain: str, stored_hash: str | bytes) -> bool:
    _require_bcrypt()
    if not stored_hash:
        return False

    if isinstance(stored_hash, str):
        stored_hash_bytes = stored_hash.encode("utf-8")
    else:
        stored_hash_bytes = stored_hash
    try:
        return bcrypt.checkpw((plain or "").encode("utf-8"), stored_hash_bytes)
    except ValueError:
        return False

def get_user_by_username(username: str) -> Optional[dict]:
    with db_conn() as conn:
        return fetch_one(conn, "SELECT * FROM USERS WHERE username = %s", (username,))

def get_user_by_id(user_id: str) -> Optional[dict]:
    with db_conn() as conn:
        return fetch_one(conn, "SELECT * FROM USERS WHERE user_id = %s", (user_id,))

def create_user(
        *,
        username: str,
        email: str,
        password: str,
        first_name: str,
        surname: str,
) -> str:
    _require_bcrypt()
    user_id = str(uuid.uuid4())
    pwd_hash = hash_password(password)

    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
        row = fetch_one(conn, "SELECT user_id FROM USERS WHERE username = %s or email = %s", (username, email))
        if row:
            raise UserAlreadyExists("Username or email already exists")
        
        execute(
            cur,
            "INSERT INTO USERS (user_id, username, email, password_hash, first_name, surname) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, username, email, pwd_hash, first_name, surname),
        )
    return user_id

def update_password(*, user_id: str, new_password: str) -> int:
    pwd_hash = hash_password(new_password)
    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
        return execute(cur, "UPDATE USERS SET password_hash = %s WHERE user_id = %s", (pwd_hash, user_id))
    
def update_profile(
        *,
        user_id: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        surname: Optional[str] = None,
) -> int:
    sets = []
    params = []

    if username is not None:
        sets.append("username=%s")
        params.append(username)
    if email is not None:
        sets.append("email=%s")
        params.append(email)
    if first_name is not None:
        sets.append("first_name=%s")
        params.append(first_name)
    if surname is not None:
        sets.append("surname=%s")
        params.append(surname)

    if not sets:
        return 0
    
    sql = "UPDATE USERS SET " + ", ".join(sets) + " WHERE user_id=%s"
    params.append(user_id)

    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
        try:
            return execute(cur, sql, tuple(params))
        except MySQLdb.IntegrityError as e:
            if getattr(e, "args", None) and e.args[0] == 1062:
                raise UserAlreadyExists("Username or email already exists")
            raise

def delete_user(user_id: str) -> int:
    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
        return execute(cur, "DELETE FROM USERS WHERE user_id = %s", (user_id,))
    
def verify_credentials(username: str, plain_password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if not user:
        return None
    if verify_password(plain_password, user.get("password_hash")):
        return user
    return None