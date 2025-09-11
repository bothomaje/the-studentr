import uuid, datetime as dt
from app.dal import users_dal, modules_dal, assignments_dal, marks_dal

def test_assignments_flow_and_colour_rules(db_conn, db_tx):
    uid = users_dal.create_user(username=f"user_{uid[:6]}", email=f"{uid[:6]}@x.com", password="A1b2C3d4!", first_name="Test", surname="Three")
    mod_id = modules_dal.create_module(user_id=uid, module_code="INF2611",
                                       module_name="Info Systems", year_mark_weight=50, exam_weight=50,
                                       min_assignments=1)

    due_date = dt.date.today()
    a_id = assignments_dal.create_assignment(
        module_id=mod_id, assignment_title="Quiz 1",
        category="Formative", assignment_type="Quiz",
        due_date=due_date, status="Not Started"
    )
    a = assignments_dal.get_assignment_by_id(a_id)
    assert a["colour"] == "Yellow"
    marks_dal.insert_mark(assignment_id=a_id, weight=10, score=None)
    assignments_dal.update_status(a_id, "Done")
    a2 = assignments_dal.get_assignment_by_id(a_id)
    assert a2["colour"] == "Orange"
    marks_dal.update_mark_score(assignment_id=a_id, score=45)
    a3 = assignments_dal.get_assignment_by_id(a_id)
    assert a3["colour"] == "Red"
    marks_dal.update_mark_score(assignment_id=a_id, score=76)
    a4 = assignments_dal.get_assignment_by_id(a_id)
    assert a4["colour"] == "Green"
    upcoming = assignments_dal.list_upcoming_for_user(user_id=uid, days=30)
    assert isinstance(upcoming, list)
