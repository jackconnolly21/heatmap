import sqlite3 as lite
from werkzeug.security import check_password_hash, generate_password_hash

con = lite.connect("test.db")

with con:
    cur = con.cursor()

    # cur.execute('''CREATE TABLE rosters
    #             (id integer PRIMARY KEY AUTOINCREMENT,
    #             firstname text,
    #             lastname text,
    #             number integer
    #             position text
    #             team text)''')

    # cur.execute('''CREATE TABLE teams
    #                 (id integer PRIMARY KEY AUTOINCREMENT,
    #                 vm_num integer NOT NULL,
    #                 name text NOT NULL)''')

    cur.execute("SELECT * FROM teams")
    print cur.fetchall()

    # cur.execute("SELECT * FROM users WHERE username='jack'")
    # rows = cur.fetchall()
    # print rows
