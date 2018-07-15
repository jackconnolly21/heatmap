import sqlalchemy
from sqlalchemy import and_, text, select
import sqlite3 as lite

import tables

# TODO: Add function to return engine (maybe in helpers?)

def __insert(engine, table, row_dict):
    return engine.execute(table.insert(), **row_dict).lastrowid

def get_teamname_by_number(engine, number):
    stmt = text("SELECT teamname FROM teams WHERE id=%d" % number)
    team = engine.execute(stmt).fetchone()[0]
    return team

def insert_upload_row(engine, row_dict):
    return __insert(engine, UPLOADS, row_dict)
