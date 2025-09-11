import uuid, datetime as dt
from app.dal import users_dal, modules_dal, assignments_dal, marks_dal

def test_marks_aggregates_and_weights(db_conn, db_tx):
    uid = users_dal.create_user(username=f"user_{uid[:6]}", email=f"{uid[:6]}@x.com", password="Str0ngPwd!", first_name="Test", surname="Four")
    mod_id = modules_dal.create_module(user_id=uid, module_code="COS2626",
                                       module_name="Networks", year_mark_weight=40, exam_weight=60,
                                       min_assignments=1)
    a1 = assignments_dal.create_assignment(module_id=mod_id, assignment_title="FA1", category="Formative", assignment_type="Quiz", due_date=dt.date.today(), status="Done")
    a2 = assignments_dal.create_assignment(module_id=mod_id, assignment_title="FA2", category="Formative", assignment_type="Project", due_date=dt.date.today(), status="Done")
    a3 = assignments_dal.create_assignment(module_id=mod_id, assignment_title="EX1", category="Exam", assignment_type="Written exam", due_date=dt.date.today(), status="Done")
    marks_dal.insert_mark(a1, weight=10, score=80)
    marks_dal.insert_mark(a2, weight=20, score=50)
    marks_dal.insert_mark(a3, weight=100, score=60)
    averages = marks_dal.compute_category_averages(module_id=mod_id)
    assert 0 <= averages["year_mark"] <= 100 and 0 <= averages["exam_mark"] <= 100
    assert averages["year_mark"] == 30
