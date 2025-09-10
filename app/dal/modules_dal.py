from __future__ import annotations

import uuid
from typing import Optional, Iterable

import MySQLdb
from app.dal.base import db_conn, db_cursor, fetch_all, fetch_one, execute, transaction

class ModuleAlreadyExists(Exception):
    pass

def list_modules_for_user(user_id: str) -> list[dict]:
    with db_conn() as conn:
        return fetch_all(
            conn,
            "SELECT module_id, module_code, module_name, "
            "       year_mark_weight, exam_weight, min_assignments, "
            "       min_year_mark, exam_subminimum, created_at, updated_at "
            "FROM MODULES WHERE user_id=%s "
            "ORDER BY module_code",
            (user_id,),
        )

def get_module_by_id(module_id: str) -> Optional[dict]:
    with db_conn() as conn:
        return fetch_one(conn, "SELECT * FROM MODULES WHERE module_id=%s", (module_id,))

def get_module_by_code(user_id: str, module_code: str) -> Optional[dict]:
    with db_conn() as conn:
        return fetch_one(conn, "SELECT * FROM MODULES WHERE user_id=%s AND module_code=%s", (user_id, module_code),)

def create_module(
        *,
        user_id: str,
        module_code: str,
        module_name: str,
        year_mark_weight: float,
        exam_weight: float,
        min_assignments: int = 1,
        min_year_mark: Optional[float] = None,
        exam_subminimum: Optional[float] = None,
) -> str:
    if round((year_mark_weight or 0) + (exam_weight or 0), 2) != 100.00:
        raise ValueError("The year mark and exam weightings do not add up to 100%.")
    if min_assignments is None or min_assignments <= 0:
        raise ValueError("Minimum assignments must be greater than zero.")
    
    module_id = str(uuid.uuid4())

    with db_conn(autocommit=False) as conn, transaction(conn). db_cursor(conn) as cur:
        exists = fetch_one(
            conn,
            "SELECT module_id FROM MODULES WHERE user_id=%s AND module_code=%s",
            (user_id, module_code),
        )
        if exists:
            raise ModuleAlreadyExists(f"Module code '{module_code}' already exists for this user.")
        
        try:
            execute(
                cur,
                "INSERT INTO MODULES "
                "(module_id, user_id, module_code, module_name, year_mark_weight, "
                "exam_weight, min_assignments, min_year_mark, exam_subminimum) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    module_id, user_id, module_code, module_name, year_mark_weight,
                    exam_weight, min_assignments, min_year_mark, exam_subminimum
                ),
            )
        except MySQLdb.IntegrityError as e:
            if getattr(e, "args", None) and e.args[0] == 1062:
                raise ModuleAlreadyExists(f"Module code '{module_code}' already exists for this user.")
            raise

    return module_id

def update_module():
    pass

def delete_module():
    pass
