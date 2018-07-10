import csv, os, sys
import sqlite3 as lite

con = lite.connect('heatmap.db')

# files = []
# for f in os.listdir(os.getcwd() + '/data/ncaam_codes/'):
#     if f.endswith('.SQ'):
#         files.append(f)

with con:
    cur = con.cursor()
    cur.execute("UPDATE teams SET league='NCAA Mens' WHERE league='mens'")
    teams = cur.fetchall()

# for f in files:
#     with con:
#         cur = con.cursor()
#         lst = f.split(" ", 1)
#         code = lst[0]
#         name = lst[1][:-3].replace("'", "")
#         stmt = "INSERT INTO teams (id, teamname, gender) VALUES (%d, '%s', '%s')" % (int(code), name, 'mens')
#         print stmt
#         cur.execute(stmt)

with con:
    cur = con.cursor()

    cur.execute("SELECT * FROM teams")
    print cur.fetchall()
