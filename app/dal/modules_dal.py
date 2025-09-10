from __future__ import annotations

import uuid
from typing import Optional, Iterable

import MySQLdb
from app.dal.base import db_conn, db_cursor, fetch_all, fetch_one, execute, transaction

class ModuleAlreadyExists(Exception):
    pass

def list_modules_for_user(user_id):
    pass

def get_module(user_id, module_code):
    pass

def create_module(module):
    pass

def update_module():
    pass

def delete_module():
    pass
