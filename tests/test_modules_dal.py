import uuid
from app.dal import modules_dal, users_dal

def test_modules_dashboard_and_crud(db_conn, db_tx):
    uid = users_dal.create_user(username=f"user_{uid[:6]}", email=f"{uid[:6]}@x.com", password="heyHey12!", first_name="Test", surname="Two")
    mod_id = modules_dal.create_module(
        user_id=uid, module_code="COS2611", module_name="Data Structures",
        year_mark_weight=40, exam_weight=60,
        min_assignments=2, min_year_mark=30, exam_subminimum=40
    )
    m = modules_dal.get_module_by_id(mod_id)
    assert m["module_code"] == "COS2611"
    dash = modules_dal.list_modules_dashboard(uid)
    assert any(d["module_id"] == mod_id for d in dash)
    modules_dal.update_module(mod_id, module_name="DSA")
    m2 = modules_dal.get_module_by_id(mod_id)
    assert m2["module_name"] == "DSA"
