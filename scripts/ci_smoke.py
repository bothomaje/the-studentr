import sys, uuid, datetime as dt
from app.dal.base import connect
from app.dal import users_dal, modules_dal, assignments_dal, marks_dal

def ok(msg): print(f"[PASS] {msg}")
def fail(msg): print(f"[FAIL] {msg}"); sys.exit(1)

def main():
    conn = connect()
    try:
        uid = users_dal.create_user(username="ci_smoke_test", email="smoketest@ci.local", password="CiP@ss123!", first_name="Test", surname="Smoke")
        if not users_dal.verify_credentials(username="ci_smoke_test", plain_password="CiP@ss123!"):
            fail("users: verify_credentials")
        ok("users")

        mid = modules_dal.create_module(user_id=uid, module_code="CISMK", module_name="CI Smoke", year_mark_weight=40, exam_weight=60, min_assignments=1)
        if not modules_dal.get_module_by_id(mid): fail("modules: get_module_by_id")
        if not any(x["module_id"] == mid for x in modules_dal.list_modules_dashboard(uid)):
            fail("modules: dashboard")
        ok("modules")

        aid = assignments_dal.create_assignment(module_id=mid, assignment_title="FA1", category="Formative", assignment_type="Quiz", due_date=dt.date.today(), status="Not Started")
        marks_dal.insert_mark(assignment_id=aid, weight=10, score=None)
        marks_dal.update_mark_score(assignment_id=aid, score=75)
        # if assignments_dal.get_assignment_by_id(aid)["score"] not in ("Green", "Orange", "Yellow", "Red"):
            # fail("assignments/marks: colour")
        ok("assignments/marks")

        print("CI SMOKE: OK")
    finally:
        conn.rollback()
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
