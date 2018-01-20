import csv, os, sys
import sqlite3 as lite

con = lite.connect('test.db')

# files = []
# for f in os.listdir(os.getcwd() + '/data/ncaam_codes'):
#     if f.endswith('.SQ'):
#         files.append(f)

# with con:
#     cur = con.cursor()
#     cur.execute("DELETE FROM teams WHERE id > 1259")
#
#     cur.execute("SELECT * FROM teams")
#     print cur.fetchall()
