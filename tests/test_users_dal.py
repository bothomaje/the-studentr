import uuid
from app.dal import users_dal

def test_users_crud_and_verify(db_conn, db_tx):
    username = "test_users_dal"
    email = "test_users_dal@example.com"
    firstname = "Test"
    surname = "One"
    user_id = users_dal.create_user(username=username, email=email, password="P@ssw0rd!", first_name=firstname, surname=surname)
    got = users_dal.get_user_by_username(username)
    assert got and got["user_id"] == user_id
    ok = users_dal.verify_credentials(username=username, plain_password="P@ssw0rd!")
    assert ok
    bad = users_dal.verify_credentials(username=username, plain_password="wrong")
    assert not bad
    new_email = "new+"+email
    users_dal.update_profile(user_id=user_id, email=new_email)
    got2 = users_dal.get_user_by_id(user_id)
    assert got2["email"].startswith("new+")
