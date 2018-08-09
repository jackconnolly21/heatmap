import sqlalchemy
from sqlalchemy import text, update, func
from sqlalchemy.sql import and_, or_, select

from tables import USERS, TEAMS, UPLOADS


# General helper functions
def __insert(engine, table, row_dict):
    return engine.execute(table.insert(), **row_dict).lastrowid


def __select_all_from_table(engine, table, order=False):
    stmt = table.select()
    if order:
        stmt = stmt.order_by(table.c.id)
    return engine.execute(stmt).fetchall()


# USERS table
def insert_user(engine, user_dict):
    return __insert(engine, USERS, user_dict)


def get_user_by_user_id(engine, user_id):
    stmt = USERS.select()
    stmt = stmt.where(USERS.c.id == user_id)
    return engine.execute(stmt).fetchone()


def get_all_users(engine):
    return __select_all_from_table(engine, USERS)


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
    return __select_all_from_table(engine, TEAMS, order=True)


def get_teams_typeahead(engine, substring, max_teams=None):
    # TODO: Make this ORM, add limit?
    stmt = TEAMS.select()
    stmt = stmt.where(TEAMS.c.teamname.ilike(substring))
    if max_teams is not None:
        stmt = stmt.limit(max_teams).order_by(func.random())
    return [dict(row) for row in engine.execute(stmt).fetchall()]


def upload_team(engine, row_dict):
    return __insert(engine, TEAMS, row_dict)


# UPLOADS table
def insert_upload_row(engine, row_dict):
    return __insert(engine, UPLOADS, row_dict)


def get_all_uploads(engine):
    return __select_all_from_table(engine, UPLOADS)
