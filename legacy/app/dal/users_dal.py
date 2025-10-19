from __future__ import annotations

import uuid
from typing import Optional

from app.dal.base import db_conn, db_query, fetch_one, execute, transaction, IntegrityError

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
    with db_conn() as db:
        return fetch_one(db, "SELECT * FROM users WHERE username = ?", (username,))

def get_user_by_id(user_id: str) -> Optional[dict]:
    with db_conn() as db:
        return fetch_one(db, "SELECT * FROM users WHERE user_id = ?", (user_id,))

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

    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        row = fetch_one(db, "SELECT user_id FROM users WHERE username = ? or email = ?", (username, email))
        if row:
            raise UserAlreadyExists("Username or email already exists")
        
        execute(
            query,
            "INSERT INTO users (user_id, username, email, password_hash, first_name, surname) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, email, pwd_hash, first_name, surname),
        )
    return user_id

def update_password(*, user_id: str, new_password: str) -> int:
    pwd_hash = hash_password(new_password)
    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        return execute(query, "UPDATE users SET password_hash = ? WHERE user_id = ?", (pwd_hash, user_id))
    
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
        sets.append("username=?")
        params.append(username)
    if email is not None:
        sets.append("email=?")
        params.append(email)
    if first_name is not None:
        sets.append("first_name=?")
        params.append(first_name)
    if surname is not None:
        sets.append("surname=?")
        params.append(surname)

    if not sets:
        return 0
    
    sql = "UPDATE users SET " + ", ".join(sets) + " WHERE user_id=?"
    params.append(user_id)

    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        try:
            return execute(query, sql, tuple(params))
        except IntegrityError as e:
            if getattr(e, "args", None) and e.args[0] == 1062:
                raise UserAlreadyExists("Username or email already exists")
            raise

def delete_user(user_id: str) -> int:
    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        return execute(query, "DELETE FROM users WHERE user_id = ?", (user_id,))
    
def verify_credentials(username: str, plain_password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if not user:
        return None
    if verify_password(plain_password, user.get("password_hash")):
        return user
    return None