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

    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
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

def update_module(
    module_id: str,
    *,
    module_code: Optional[str] = None,
    module_name: Optional[str] = None,
    year_mark_weight: Optional[float] = None,
    exam_weight: Optional[float] = None,
    min_assignments: Optional[int] = None,
    min_year_mark: Optional[float] = None,
    exam_subminimum: Optional[float] = None,
) -> int:
    if year_mark_weight is not None or exam_weight is not None:
        row = get_module_by_id(module_id)
        if not row:
            return 0
        y = year_mark_weight if year_mark_weight is not None else float(row["year_mark_weight"])
        e = exam_weight if exam_weight is not None else float(row["exam_weight"])
        if round(y + e, 2) != 100.00:
            raise ValueError("year_mark_weight + exam_weight must equal 100")

    sets, params = [], []
    def add(col: str, val):
        sets.append(f"{col}=%s")
        params.append(val)

    if module_code is not None: add("module_code", module_code)
    if module_name is not None: add("module_name", module_name)
    if year_mark_weight is not None: add("year_mark_weight", year_mark_weight)
    if exam_weight is not None: add("exam_weight", exam_weight)
    if min_assignments is not None: add("min_assignments", min_assignments)
    if min_year_mark is not None: add("min_year_mark", min_year_mark)
    if exam_subminimum is not None: add("exam_subminimum", exam_subminimum)

    if not sets:
        return 0

    sql = "UPDATE MODULES SET " + ", ".join(sets) + " WHERE module_id=%s"
    params.append(module_id)

    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
        try:
            return execute(cur, sql, tuple(params))
        except MySQLdb.IntegrityError as e:
            if getattr(e, "args", None) and e.args[0] == 1062:
                raise ModuleAlreadyExists("Module code already exists for this user") from e
            raise

def delete_module(module_id: str) -> int:
    with db_conn(autocommit=False) as conn, transaction(conn), db_cursor(conn) as cur:
        return execute(cur, "DELETE FROM MODULES WHERE module_id=%s", (module_id,))
    
def list_modules_dashboard(user_id: str) -> list[dict]:
    sql = """
    SELECT
      m.module_id,
      m.module_code,
      m.module_name,
      m.year_mark_weight, m.exam_weight,
      m.min_assignments, m.min_year_mark, m.exam_subminimum,
      -- counts
      SUM(a.category='Formative')                 AS total_formative,
      SUM(a.category='Formative' AND a.status='Done') AS formative_done,
      SUM(a.category='Exam')                      AS total_exams,
      SUM(a.category='Exam' AND a.status='Done')  AS exams_done,
      -- weighted category averages (NULL if no scored marks)
      ROUND(
        CASE WHEN SUM(CASE WHEN a.category='Formative' AND mk.score IS NOT NULL THEN mk.weight END) > 0
             THEN SUM(CASE WHEN a.category='Formative' AND mk.score IS NOT NULL THEN mk.score * mk.weight END)
                /  SUM(CASE WHEN a.category='Formative' AND mk.score IS NOT NULL THEN mk.weight END)
             ELSE NULL END, 2
      ) AS year_mark,
      ROUND(
        CASE WHEN SUM(CASE WHEN a.category='Exam' AND mk.score IS NOT NULL THEN mk.weight END) > 0
             THEN SUM(CASE WHEN a.category='Exam' AND mk.score IS NOT NULL THEN mk.score * mk.weight END)
                /  SUM(CASE WHEN a.category='Exam' AND mk.score IS NOT NULL THEN mk.weight END)
             ELSE NULL END, 2
      ) AS exam_mark
    FROM MODULES m
    LEFT JOIN ASSIGNMENTS a ON a.module_id = m.module_id
    LEFT JOIN MARKS mk       ON mk.assignment_id = a.assignment_id
    WHERE m.user_id = %s
    GROUP BY m.module_id
    ORDER BY m.module_code
    """
    with db_conn() as conn:
        rows = fetch_all(conn, sql, (user_id,))

    # compute final + booleans in Python for clarity
    out = []
    for r in rows:
        yw = float(r["year_mark_weight"])
        ew = float(r["exam_weight"])
        y  = r["year_mark"]
        e  = r["exam_mark"]

        final_mark = None
        if y is not None and e is not None:
            final_mark = round((y * yw + e * ew) / 100.0, 2)

        # Admission: min assignments (formative 'Done') and optional min_year_mark
        formative_done = int(r.get("formative_done") or 0)
        min_assign     = int(r.get("min_assignments") or 0)
        min_year       = r.get("min_year_mark")  # may be None
        admission_ok   = (formative_done >= min_assign) and (min_year is None or (y is not None and y >= float(min_year)))

        # Exam subminimum
        submin = r.get("exam_subminimum")  # may be None
        exam_submin_met = (submin is None) or (e is not None and e >= float(submin))

        out.append({
            "module_id": r["module_id"],
            "module_code": r["module_code"],
            "module_name": r["module_name"],
            "year_mark_weight": yw,
            "exam_weight": ew,
            "min_assignments": min_assign,
            "min_year_mark": float(min_year) if min_year is not None else None,
            "exam_subminimum": float(submin) if submin is not None else None,
            "total_formative": int(r.get("total_formative") or 0),
            "formative_done": formative_done,
            "total_exams": int(r.get("total_exams") or 0),
            "exams_done": int(r.get("exams_done") or 0),
            "year_mark": float(y) if y is not None else None,
            "exam_mark": float(e) if e is not None else None,
            "final_mark": final_mark,
            "admission_ok": bool(admission_ok),
            "exam_submin_met": bool(exam_submin_met),
        })
    return out
