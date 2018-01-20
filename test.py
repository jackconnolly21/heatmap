import sqlite3 as lite
from werkzeug.security import check_password_hash, generate_password_hash
import helpers

con = lite.connect("test.db")
cur = con.cursor()
rows = cur.execute("SELECT * FROM teams").fetchall()
print rows
