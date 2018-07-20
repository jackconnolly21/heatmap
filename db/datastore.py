import sqlalchemy
from sqlalchemy import text, update
from sqlalchemy.sql import and_, or_, select
import sqlite3 as lite

from tables import USERS, TEAMS, UPLOADS

# General helper functions
def __insert(engine, table, row_dict):
    return engine.execute(table.insert(), **row_dict).lastrowid

# USERS table
def insert_user(engine, user_dict):
    return __insert(engine, USERS, user_dict)

def get_user_by_user_id(engine, user_id):
    stmt = USERS.select()
    stmt = stmt.where(USERS.c.id == user_id)
    return engine.execute(stmt).fetchone()

def get_user_by_username(engine, username):
    stmt = USERS.select()
    stmt = stmt.where(USERS.c.username == username)
    return engine.execute(stmt).fetchone()

def update_password_hash(engine, user_id, pw_hash):
    stmt = USERS.update()
    stmt = stmt.where(USERS.c.id == user_id)
    stmt = stmt.values({'hash': pw_hash})
    return engine.execute(stmt)

# TEAMS table
def get_teamname_by_number(engine, number):
    stmt = select([TEAMS.c.teamname])
    stmt = stmt.where(TEAMS.c.id == number)
    return engine.execute(stmt).fetchone()[0]

def get_all_teams(engine):
    stmt = TEAMS.select().order_by(TEAMS.c.id)
    return engine.execute(stmt).fetchall()

def get_teams_typeahead(engine, substring, limit=10):
    # TODO: Make this ORM
    stmt = text('SELECT * FROM teams WHERE teamname LIKE %s ORDER BY RANDOM() LIMIT 10' % (substring))
    teams = engine.execute(stmt).fetchall()
    return [{'vm_num': row['id'], 'name': row['teamname']} for row in teams]

# UPLOADS table
def insert_upload_row(engine, row_dict):
    return __insert(engine, UPLOADS, row_dict)
