from __future__ import annotations

import uuid
from typing import Optional

from app.dal.base import db_conn, db_query, fetch_all, fetch_one, execute, transaction, IntegrityError

def _validate_weight(weight: float) -> None:
    if weight is None or weight < 0 or weight > 100:
        raise ValueError("weight must be between 0 and 100")

def _validate_score(score: Optional[float]) -> None:
    if score is None:
        return
    if score < 0 or score > 100:
        raise ValueError("score must be between 0 and 100")

def get_mark_by_assignment(assignment_id: str) -> Optional[dict]:
    sql = """
    SELECT mk.mark_id, mk.assignment_id, mk.weight, mk.score,
           a.module_id, a.category, a.assignment_title
    FROM marks mk
    JOIN assignments a ON a.assignment_id = mk.assignment_id
    WHERE mk.assignment_id = ?
    """
    with db_conn() as db:
        return fetch_one(db, sql, (assignment_id,))

def list_marks_for_module(module_id: str) -> list[dict]:
    sql = """
    SELECT mk.mark_id, mk.assignment_id, mk.weight, mk.score,
           a.category, a.assignment_type, a.assignment_title, a.due_date, a.due_time, a.submit_status
    FROM assignments a
    LEFT JOIN marks mk ON mk.assignment_id = a.assignment_id
    WHERE a.module_id = ?
    ORDER BY a.category, a.due_date, a.due_time
    """
    with db_conn() as db:
        return fetch_all(db, sql, (module_id,))

def insert_mark(*, assignment_id: str, weight: float, score: Optional[float] = None) -> str:
    _validate_weight(weight)
    _validate_score(score)

    with db_conn(autocommit=False) as db, transaction(db):
        row = fetch_one(db, "SELECT mark_id FROM marks WHERE assignment_id=?", (assignment_id,))
        if row:
            with db_query(db) as query:
                execute(query, "UPDATE marks SET weight=?, score=? WHERE assignment_id=?",
                        (weight, score, assignment_id))
            return row["mark_id"]

        mark_id = str(uuid.uuid4())
        with db_query(db) as query:
            try:
                execute(query,
                        "INSERT INTO marks (mark_id, assignment_id, weight, score) "
                        "VALUES (?, ?, ?, ?)",
                        (mark_id, assignment_id, weight, score))
            except IntegrityError as e:
                if getattr(e, "args", None) and e.args[0] in (1452, 1062):
                    raise ValueError("Invalid assignment_id (FK) or duplicate mark") from e
                raise
        return mark_id

def update_mark_score(*, assignment_id: str, score: Optional[float]) -> int:
    _validate_score(score)
    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        return execute(query, "UPDATE marks SET score=? WHERE assignment_id=?", (score, assignment_id))

def update_mark_weight(*, assignment_id: str, weight: float) -> int:
    _validate_weight(weight)
    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        return execute(query, "UPDATE marks SET weight=? WHERE assignment_id=?", (weight, assignment_id))

def delete_mark_by_assignment(assignment_id: str) -> int:
    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        return execute(query, "DELETE FROM marks WHERE assignment_id=?", (assignment_id,))