import csv, os, sys
import sqlite3 as lite

con = lite.connect('test.db')

files = []
for f in os.listdir(os.getcwd() + '/ncaaw_codes/teams'):
    if f.endswith('.SQ'):
        files.append(f)

with con:
    cur = con.cursor()
    # for f in files:
    #     f = f[:-3]
    #     s = f.split(" ", 1)
    #     cur.execute("INSERT INTO teams (vm_num, name) VALUES (?, ?)", (int(s[0]), s[1]))
    #     con.commit()

    cur.execute("SELECT * FROM teams")
    print cur.fetchall()
