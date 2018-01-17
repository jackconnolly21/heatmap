from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_jsglue import JSGlue
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import gettempdir
from datetime import datetime
import sqlite3 as lite
import sys, os, heatMap
from parser import Parser

from helpers import *

app = Flask(__name__)
JSGlue(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con = lite.connect('test.db')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/heatmap", methods=["GET", "POST"])
def heatmap():
    if request.method == "POST":
        team = int(request.form.get("teamname"))
        player = int(request.form.get("player"))
        attacks = request.form.get("attacks").split(",")
        if request.form.get("kills"):
            onlyKills = True
        else:
            onlyKills = False

        files = []
        for f in os.listdir(os.getcwd() + '/data/testdata'):
            if f.endswith('.dvw'):
                files.append(f)

        locations = []
        for fileName in files:
            parser = Parser(fileName)
            locations = parser.getAttackInfo(team, player, attacks, locations, onlyKills)

        heatMap.drawHeatMap(locations)

        return render_template("heatmap.html")

    else:
        return render_template("heatmap.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username

        cur = con.cursor()

        cur.execute("SELECT * FROM users WHERE username=:username",
                          {"username":request.form.get("username")})

        rows = cur.fetchall()

        # ensure username exists and password hash is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0][0]

        con.close()
        # redirect user to index
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register User"""

    session.clear()

    if request.method == "POST":
        # check that username was provided
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # check that name was provided
        elif not request.form.get("name"):
            return apology("must provide name", 403)
        # check that password was provided twice
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password twice", 403)
        # check that both passwords match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords must match", 403)

        with con:

            # Add user to database
            cur = con.cursor()
            cur.execute("SELECT * FROM users")

            user = (request.form.get("username"),
                    generate_password_hash(request.form.get("password")),
                    request.form.get("name"))
            id = create_user(con, user)

            # if not id:
            #     return apology("username taken")

            session["user_id"] = id

        # redirect to index
        flash("You are registered!")
        return redirect(url_for("index"))

    else:
        return render_template("register.html")

@app.route("/password")
@login_required
def password():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
