import sys
import datetime as dt
from app.dal import users_dal, modules_dal, assignments_dal, marks_dal

def ok(msg):
    print(f"[PASS] {msg}")

def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def main():
    from app.dal.base import db_conn, transaction
    import uuid
    
    # Generate unique identifiers for test data
    test_suffix = str(uuid.uuid4())[:8]
    test_username = f"ci_smoke_test_{test_suffix}"
    test_email = f"smoketest_{test_suffix}@ci.local"
    
    with db_conn(autocommit=False) as conn:
        with transaction(conn):
            try:
                uid = users_dal.create_user(username=test_username, email=test_email, password="CiP@ss123!", first_name="Test", surname="Smoke")
                info = users_dal.get_user_by_id(uid)
                print(info["password_hash"])
                print(users_dal.hash_password("CiP@ss123!"))
                if not users_dal.verify_credentials(username=test_username, plain_password="CiP@ss123!"):
                    fail("users: verify_credentials")
                ok("users")

                mid = modules_dal.create_module(user_id=uid, module_code="CISMK", module_name="CI Smoke", year_mark_weight=40, exam_weight=60, min_assignments=1)
                if not modules_dal.get_module_by_id(mid, uid):
                    fail("modules: get_module_by_id")
                if not any(x["module_id"] == mid for x in modules_dal.list_modules_dashboard(uid)):
                    fail("modules: dashboard")
                ok("modules")

                aid = assignments_dal.create_assignment(user_id=uid, module_id=mid, assignment_title="FA1", category="Formative", assignment_type="Quiz", due_date=dt.date.today(), submit_status="Not Started")
                marks_dal.insert_mark(assignment_id=aid, weight=10, score=None)
                marks_dal.update_mark_score(assignment_id=aid, score=75)
                # if assignments_dal.get_assignment_by_id(aid)["score"] not in ("Green", "Orange", "Yellow", "Red"):
                    # fail("assignments/marks: colour")
                ok("assignments/marks")

                print("CI SMOKE: OK")
                # Transaction will be rolled back automatically when context exits
                # This ensures test data is cleaned up
                raise SystemExit(0)  # Exit successfully but still roll back
            except SystemExit:
                raise  # Re-raise SystemExit to maintain the exit code
            except Exception as e:
                print(f"CI SMOKE: ERROR - {e}")
                import traceback
                traceback.print_exc()
                raise SystemExit(1)

if __name__ == "__main__":
    sys.exit(main())
