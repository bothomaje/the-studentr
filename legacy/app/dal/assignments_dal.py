from __future__ import annotations

import uuid
from datetime import date, time
from typing import Optional, Literal

from app.dal.base import db_conn, db_query, fetch_all, fetch_one, execute, transaction, IntegrityError


Status = Literal["Not Started", "In Progress", "Done", "Skipped"]
Category = Literal["Formative", "Exam"]

STATUS_VALUES: set[str]   = {"Not Started", "In Progress", "Done", "Skipped"}
CATEGORY_VALUES: set[str] = {"Formative", "Exam"}
TYPES_BY_CATEGORY: dict[str, set[str]] = {
    "Formative": {"Quiz", "Written assignment", "Practical"},
    "Exam": {"Quiz", "Written exam", "Take-Home exam"},
}

def _validate_submit_status(submit_status: str) -> None:
    if submit_status not in STATUS_VALUES:
        raise ValueError(f"Invalid status '{submit_status}'")

def _validate_category_type(category: str, assignment_type: str) -> None:
    if category not in CATEGORY_VALUES:
        raise ValueError(f"Invalid category '{category}'")
    allowed = TYPES_BY_CATEGORY[category]
    if assignment_type not in allowed:
        raise ValueError(
            f"assignment_type '{assignment_type}' not valid for category '{category}'. "
            f"Allowed: {sorted(allowed)}"
        )

def _colour_from(submit_status: str, score: Optional[float]) -> str:
    if submit_status != "Done":
        return "Yellow"
    if score is None:
        return "Orange"
    return "Green" if score >= 50.0 else "Red"

def get_assignment_by_id(assignment_id: str, user_id: str) -> Optional[dict]:
    with db_conn() as db:
        return fetch_one(db, 
                         "SELECT a.* "
                         "FROM assignments a "
                         "JOIN modules m ON m.module_id=a.module_id "
                         "WHERE assignment_id=? AND user_id=?", 
                         (assignment_id, user_id),)

def list_assignments_for_module(
    module_id: str,
    user_id: str,
    *,
    submit_status: Optional[Status] = None,
    category: Optional[Category] = None,
    include_marks: bool = True,
    order_by_due: bool = True,
) -> list[dict]:
    params: list = [module_id, user_id]
    where = ["a.module_id=?", "m.user_id=?"]

    if submit_status:
        _validate_submit_status(submit_status)
        where.append("a.submit_status=?")
        params.append(submit_status)
    if category:
        if category not in CATEGORY_VALUES:
            raise ValueError("Invalid category")
        where.append("a.category=?")
        params.append(category)

    join = "JOIN modules m ON m.module_id = a.module_id "
    join = join + ("LEFT JOIN marks mk ON mk.assignment_id=a.assignment_id" if include_marks else "")
    select_marks = ", mk.weight, mk.score" if include_marks else ""
    order = "ORDER BY a.due_date, a.due_time" if order_by_due else "ORDER BY a.created_at"

    sql = f"""
    SELECT
      a.assignment_id, a.module_id, a.category, a.assignment_type,
      a.assignment_title, a.start_date, a.due_date, a.due_time,
      a.submit_date, a.submit_status, a.created_at, a.updated_at
      {select_marks}
    FROM assignments a
    {join}
    WHERE {" AND ".join(where)}
    {order}
    """
    with db_conn() as db:
        rows = fetch_all(db, sql, tuple(params))

    if include_marks:
        for r in rows:
            r["colour"] = _colour_from(r["submit_status"], r.get("score"))
    return rows

def list_upcoming_for_user(
    user_id: str,
    *,
    days: int = 14,
    include_overdue: bool = False,
) -> list[dict]:
    comparator = "<=" if include_overdue else ">="
    sql = f"""
    SELECT
      a.assignment_id, a.category, a.assignment_type, a.assignment_title,
      a.due_date, a.due_time, a.submit_status,
      m.module_id, m.module_code, m.module_name,
      mk.weight, mk.score
    FROM modules m
    JOIN assignments a ON a.module_id = m.module_id
    LEFT JOIN marks mk ON mk.assignment_id = a.assignment_id
    WHERE m.user_id = ?
      AND TIMESTAMP(a.due_date, COALESCE(a.due_time,'23:59:00')) {comparator} NOW()
      AND TIMESTAMP(a.due_date, COALESCE(a.due_time,'23:59:00')) <= NOW() + INTERVAL ? DAY
    ORDER BY a.due_date, a.due_time
    """
    with db_conn() as db:
        rows = fetch_all(db, sql, (user_id, days))
    for r in rows:
        r["colour"] = _colour_from(r["submit_status"], r.get("score"))
    return rows

def count_by_submit_status_for_module(module_id: str) -> dict[str, int]:
    sql = """
    SELECT a.submit_status, COUNT(*) AS c
    FROM assignments a
    WHERE a.module_id=?
    GROUP BY a.submit_status
    """
    with db_conn() as db:
        rows = fetch_all(db, sql, (module_id,))
    return {r["submit_status"]: int(r["c"]) for r in rows}

def create_assignment(
    *,
    user_id: str,
    module_id: str,
    category: Category,
    assignment_type: str,
    assignment_title: str,
    start_date: Optional[date] = None,
    due_date: date,
    due_time: Optional[time] = "23:59:00",
    submit_date: Optional[date] = None,
    submit_status: Status = "Not Started",
) -> str:
    _validate_submit_status(submit_status)
    _validate_category_type(category, assignment_type)

    assignment_id = str(uuid.uuid4())

    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        try:
            execute(
                query,
                "INSERT INTO assignments "
                "(assignment_id, module_id, category, assignment_type, assignment_title, "
                "start_date, due_date, due_time, submit_date, submit_status) "
                "SELECT ?, m.module_id, ?, ?, ?, ?, ?, ?, ?, ? "
                "FROM modules m WHERE m.module_id=? AND user_id=?",
                (
                    assignment_id, category, assignment_type, assignment_title,
                    start_date, due_date, due_time, submit_date, submit_status, module_id, user_id,
                ),
            )
        except IntegrityError as e:
            if getattr(e, "args", None) and e.args[0] in (1452,):
                raise ValueError("Invalid module_id (FK)") from e
            raise
    return assignment_id

def update_assignment(
    assignment_id: str,
    *,
    category: Optional[Category] = None,
    assignment_type: Optional[str] = None,
    assignment_title: Optional[str] = None,
    start_date: Optional[date] = None,
    due_date: Optional[date] = None,
    due_time: Optional[time] = None,
    submit_date: Optional[date] = None,
    submit_status: Optional[Status] = None,
) -> int:
    if submit_status is not None:
        _validate_submit_status(submit_status)
    if category is not None or assignment_type is not None:
        cat = category
        typ = assignment_type
        if cat is None or typ is None:
            row = get_assignment_by_id(assignment_id)
            if not row:
                return 0
            if cat is None:
                cat = row["category"]
            if typ is None:
                typ = row["assignment_type"]
        _validate_category_type(cat, typ)

    sets, params = [], []

    def add(col: str, val):
        sets.append(f"{col}=?")
        params.append(val)

    if category is not None:
        add("category", category)
    if assignment_type is not None:
        add("assignment_type", assignment_type)
    if assignment_title is not None:
        add("assignment_title", assignment_title)
    if start_date is not None:
        add("start_date", start_date)
    if due_date is not None:
        add("due_date", due_date)
    if due_time is not None:
        add("due_time", due_time)
    if submit_date is not None:
        add("submit_date", submit_date)
    if submit_status is not None:
        add("submit_status", submit_status)

    if not sets:
        return 0

    sql = "UPDATE assignments SET " + ", ".join(sets) + " WHERE assignment_id=?"
    params.append(assignment_id)

    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        return execute(query, sql, tuple(params))

def update_submit_status(assignment_id: str, submit_status: Status) -> int:
    _validate_submit_status(submit_status)
    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        return execute(query, "UPDATE assignments SET submit_status=? WHERE assignment_id=?", (submit_status, assignment_id))

def delete_assignment(assignment_id: str) -> int:
    with db_conn(autocommit=False) as db, transaction(db), db_query(db) as query:
        return execute(query, "DELETE FROM assignments WHERE assignment_id=?", (assignment_id,))
