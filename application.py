import sys, os, heatMap
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_jsglue import JSGlue
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from tempfile import gettempdir
from datetime import datetime
import sqlite3 as lite

from db import datastore
from helpers import *
from parser import Parser

app = Flask(__name__)
JSGlue(app)

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure app for uploads
UPLOAD_FOLDER = 'data/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = get_db_engine()

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/heatmap", methods=["POST"])
@login_required
def heatmap():
    team = int(request.form.get("teamname"))
    player = int(request.form.get("player"))
    attacks = request.form.get("attacks").split(",")
    data = request.form.get("datafiles")

    if request.form.get("kills"):
        onlyKills = True
    else:
        onlyKills = False

    files = []
    folder = 'data/' + data
    for f in os.listdir(os.getcwd() + '/' + folder):
        if f.endswith('.dvw'):
            files.append(folder + '/' + f)

    locations = []
    for fileName in files:
        parser = Parser(fileName)
        locations = parser.getAttackInfo(team, player, attacks, locations, onlyKills)

    top_caption, bottom_caption = generate_caption(team, player, attacks, onlyKills)
    output_url = generate_output_filename(team, player, attacks, onlyKills)
    output_dict = heatMap.drawArcsPillow(locations, output_url, top_caption=top_caption, bottom_caption=bottom_caption)

    result_dict = {
        'output_url': output_url,
        'width': output_dict['width'],
        'height': output_dict['height'],
    }
    return render_template("heatmap.html", result_dict=result_dict)

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if 'dvwfile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['dvwfile']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = '_'.join('user', session['user_id'], secure_filename(file.filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            upload_dict = {'user_id': session['user_id'], 'file_key': filename}
            datastore.insert_upload_row(engine, upload_dict)

            flash("File Uploaded!")
        return redirect(url_for("upload"))
    else:
        return render_template("upload.html")

@app.route("/teams")
def teams():

    substring = "%" + request.args.get("t") + "%"

    team_list = datastore.get_teams_typeahead(engine, substring, limit=10)

    print team_list
    return jsonify(team_list)

@app.route("/info")
@login_required
def info():

    teams = datastore.get_all_teams(engine)

    teamList = []
    for team in teams:
        teamDict = {
            "id": team[0],
            "name": team[1],
            "league": team[2]
        }
        teamList.append(teamDict)

    return render_template("info.html", rows=teamList)


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

        # Query database for user
        user = datastore.get_user_by_username(engine, request.form.get("username"))

        # ensure username exists and password hash is correct
        if user is None or not check_password_hash(user['hash'], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = user['id']

        # redirect user to index
        flash('Logged in!')
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
        elif not request.form.get("firstname") or not request.form.get("lastname"):
            return apology("must provide full name", 403)
        # check that password was provided twice
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password twice", 403)
        # check that both passwords match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords must match", 403)

        user_dict = {
            'username': request.form.get('username'),
            'hash': generate_password_hash(request.form.get('password')),
            'firstname': request.form.get('firstname'),
            'lastname': request.form.get('lastname')
        }
        user_id = datastore.insert_user(engine, user_dict)

        if not user_id:
            return apology("username taken")

        session["user_id"] = user_id

        # redirect to index
        flash("You are registered!")
        return redirect(url_for("index"))

    else:
        return render_template("register.html")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Allow user to change password"""

    if request.method == "POST":
        print "Changing password"
        # query for user's hash of password
        pw_hash = datastore.get_user_by_user_id(engine, session['user_id'])['hash']

        # check all boxes filled, old password is correct, new and confirmation match
        if not request.form.get("old") or not check_password_hash(pw_hash, request.form.get("old")):
            return apology("incorrect password")
        elif not request.form.get("new") or not request.form.get("confirmation"):
            return apology("must type new password twice")
        elif not request.form.get("new") == request.form.get("confirmation"):
            return apology("new passwords must match")

        # update hash in database
        datastore.update_password_hash(engine, session['user_id'], pw_hash)

        # redirect to portfolio
        flash("Password changed!")
        print "Password changed!"
        return redirect(url_for("index"))

    else:
        return render_template("password.html")
