from __future__ import annotations

import uuid
from typing import Optional, Tuple

import MySQLdb
from app.dal.base import db_conn, db_cursor, fetch_all, fetch_one, execute, transaction, insert_one

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
    FROM MARKS mk
    JOIN ASSIGNMENTS a ON a.assignment_id = mk.assignment_id
    WHERE mk.assignment_id = %s
    """
    with db_conn() as conn:
        return fetch_one(conn, sql, (assignment_id,))

def list_marks_for_module(module_id: str) -> list[dict]:
    sql = """
    SELECT mk.mark_id, mk.assignment_id, mk.weight, mk.score,
           a.category, a.assignment_type, a.assignment_title, a.due_date, a.due_time, a.status
    FROM ASSIGNMENTS a
    LEFT JOIN MARKS mk ON mk.assignment_id = a.assignment_id
    WHERE a.module_id = %s
    ORDER BY a.category, a.due_date, a.due_time
    """
    with db_conn() as conn:
        return fetch_all(conn, sql, (module_id,))

def insert_mark(*, assignment_id: str, weight: float, score: Optional[float] = None) -> str:
    _validate_weight(weight)
    _validate_score(score)

    with db_conn(autocommit=False) as conn, transaction(conn):
        row = fetch_one(conn, "SELECT mark_id FROM MARKS WHERE assignment_id=%s", (assignment_id,))
        if row:
            with db_cursor(conn) as cur:
                execute(cur, "UPDATE MARKS SET weight=%s, score=%s WHERE assignment_id=%s",
                        (weight, score, assignment_id))
            return row["mark_id"]

        mark_id = str(uuid.uuid4())
        with db_cursor(conn) as cur:
            try:
                execute(cur,
                        "INSERT INTO MARKS (mark_id, assignment_id, weight, score) "
                        "VALUES (%s, %s, %s, %s)",
                        (mark_id, assignment_id, weight, score))
            except MySQLdb.IntegrityError as e:
                if getattr(e, "args", None) and e.args[0] in (1452, 1062):
                    raise ValueError("Invalid assignment_id (FK) or duplicate mark") from e
                raise
        return mark_id

def update_mark_score(*, assignment_id: str, score: Optional[float]) -> int:
    _validate_score(score)
    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
        return execute(cur, "UPDATE MARKS SET score=%s WHERE assignment_id=%s", (score, assignment_id))

def update_mark_weight(*, assignment_id: str, weight: float) -> int:
    _validate_weight(weight)
    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
        return execute(cur, "UPDATE MARKS SET weight=%s WHERE assignment_id=%s", (weight, assignment_id))

def delete_mark_by_assignment(assignment_id: str) -> int:
    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
        return execute(cur, "DELETE FROM MARKS WHERE assignment_id=%s", (assignment_id,))

def compute_category_averages(module_id: str) -> dict:
    sql = """
    SELECT
      SUM(CASE WHEN a.category='Formative' AND mk.score IS NOT NULL THEN mk.weight END)   AS f_w,
      SUM(CASE WHEN a.category='Formative' AND mk.score IS NOT NULL THEN mk.score*mk.weight END) AS f_ws,
      SUM(CASE WHEN a.category='Exam' AND mk.score IS NOT NULL THEN mk.weight END)        AS e_w,
      SUM(CASE WHEN a.category='Exam' AND mk.score IS NOT NULL THEN mk.score*mk.weight END)      AS e_ws
    FROM ASSIGNMENTS a
    LEFT JOIN MARKS mk ON mk.assignment_id=a.assignment_id
    WHERE a.module_id=%s
    """
    with db_conn() as conn:
        r = fetch_one(conn, sql, (module_id,))
    def _avg(ws, w) -> Optional[float]:
        if ws is None or w in (None, 0):
            return None
        return round(float(ws) / float(w), 2)
    return {
        "year_mark": _avg(r["f_ws"], r["f_w"]),
        "exam_mark": _avg(r["e_ws"], r["e_w"]),
    }

def weight_totals_by_category(module_id: str) -> dict:
    sql = """
    SELECT a.category, COALESCE(SUM(mk.weight), 0) AS w_sum
    FROM ASSIGNMENTS a
    LEFT JOIN MARKS mk ON mk.assignment_id=a.assignment_id
    WHERE a.module_id=%s
    GROUP BY a.category
    """
    with db_conn() as conn:
        rows = fetch_all(conn, sql, (module_id,))
    return {r["category"]: float(r["w_sum"]) for r in rows}
