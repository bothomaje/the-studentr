import datetime as dt
from app.dal import users_dal, modules_dal, assignments_dal, marks_dal

def test_marks_aggregates_and_weights(db_conn, db_tx):
    uid = users_dal.create_user(username="user_marks_test", email="marks_test@x.com", password="Str0ngPwd!", first_name="Test", surname="Four")
    mod_id = modules_dal.create_module(user_id=uid, module_code="COS2626",
                                       module_name="Networks", year_mark_weight=40, exam_weight=60,
                                       min_assignments=1)
    a1 = assignments_dal.create_assignment(user_id=uid, module_id=mod_id, assignment_title="FA1", category="Formative", assignment_type="Quiz", due_date=dt.date.today(), status="Done")
    a2 = assignments_dal.create_assignment(user_id=uid, module_id=mod_id, assignment_title="FA2", category="Formative", assignment_type="Practical", due_date=dt.date.today(), status="Done")
    a3 = assignments_dal.create_assignment(user_id=uid, module_id=mod_id, assignment_title="EX1", category="Exam", assignment_type="Written exam", due_date=dt.date.today(), status="Done")
    marks_dal.insert_mark(assignment_id=a1, weight=10, score=80)
    marks_dal.insert_mark(assignment_id=a2, weight=20, score=50)
    marks_dal.insert_mark(assignment_id=a3, weight=100, score=60)
    mark1 = marks_dal.get_mark_by_assignment(a1)
    mark2 = marks_dal.get_mark_by_assignment(a2)
    mark3 = marks_dal.get_mark_by_assignment(a3)
    assert mark1 and mark1["weight"] == 10 and mark1["score"] == 80
    assert mark2 and mark2["weight"] == 20 and mark2["score"] == 50
    assert mark3 and mark3["weight"] == 100 and mark3["score"] == 60
