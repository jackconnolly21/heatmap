import datetime

import enum
import sqlalchemy as sql
from sqlalchemy.schema import ForeignKey
from sqlalchemy.dialects import sqlite

metadata = sql.MetaData()

USERS = sql.Table('users', metadata,
                  sql.Column('id', sql.Integer, primary_key=True),
                  sql.Column('username', sql.Text, nullable=False, unique=True),
                  sql.Column('hash', sql.Text, nullable=False),
                  sql.Column('firstname', sql.Text),
                  sql.Column('lastname', sql.Text)
                  )

TEAMS = sql.Table('teams', metadata,
                  sql.Column('id', sql.Integer, nullable=False, unique=True),
                  sql.Column('teamname', sql.Text, nullable=False),
                  sql.Column('league', sql.Text, nullable=False)
                  )

UPLOADS = sql.Table('uploads', metadata,
                  sql.Column('id', sql.Integer, primary_key=True),
                  sql.Column('user_id', sql.Integer, ForeignKey(USERS.c.id), nullable=False),
                  sql.Column('file_key', sql.Text, nullable=False),
                  )
