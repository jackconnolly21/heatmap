import os
import sqlalchemy
import sqlite3 as lite
from datetime import datetime
from flask import redirect, render_template, request, session, url_for, make_response
from functools import wraps, update_wrapper, reduce


from db import datastore

def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=url_for("index")))
        return f(*args, **kwargs)
    return decorated_function

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['dvw'])
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_engine():
    return sqlalchemy.create_engine("sqlite:///db/heatmap.db")

def attacks_to_string(attacks):
    return reduce(lambda x, y: str(x) + "-" + str(y), attacks)

def generate_output_filename(team, player, attacks, kills):
    output_folder = 'static/images/output/'
    attacks = attacks_to_string(attacks)
    filename = 'output_team_%d_player_%d_attacks_%s_kills_%s.png' % (team, player, attacks, kills)
    return output_folder + filename

def generate_caption(team, player, attacks, kills):
    engine = get_db_engine()
    attacks_str = attacks_to_string(attacks)
    teamname = datastore.get_teamname_by_number(engine, team)
    top_caption = "%s #%d" % (teamname, player)
    bottom_caption = "Attacks: %s" % (attacks_str)
    if kills:
        bottom_caption += " (Only Kills)"
    return (top_caption, bottom_caption)
