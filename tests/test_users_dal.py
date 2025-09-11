import uuid
from app.dal import users_dal

def test_users_crud_and_verify(db_conn, db_tx):
    username = f"test_{user_id[:8]}"
    email = f"{user_id[:8]}@example.com"
    firstname = "Test"
    surname = "One"
    user_id = users_dal.create_user(user_id=user_id, username=username, email=email, password="P@ssw0rd!", first_name=firstname, surname=surname)
    got = users_dal.get_user_by_username(username)
    assert got and got["user_id"] == user_id
    ok = users_dal.verify_credentials(username=username, plain_password="P@ssw0rd!")
    assert ok is True
    bad = users_dal.verify_credentials(username=username, plain_password="wrong")
    assert bad is False
    users_dal.update_profile(user_id, email="new+"+email)
    got2 = users_dal.get_user_by_id(user_id)
    assert got2["email"].startswith("new+")
