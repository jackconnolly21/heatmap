import os
import subprocess
import sqlalchemy
from datetime import datetime
from flask import redirect, session, url_for, make_response
from functools import wraps, update_wrapper, reduce

import datastore


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login', next=url_for('index')))
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
    allowed_extensions = ['dvw']
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_db_url_prod():
    # proc1 = subprocess.Popen(['heroku', 'config', '-a', 'volleyball-heatmap'], stdout=subprocess.PIPE)
    # proc2 = subprocess.Popen(['grep', 'DATABASE_URL'], stdin=proc1.stdout,
    #                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 
    # proc1.stdout.close()
    # out, err = proc2.communicate()
    # db_url = out.split(" ")[-1]
    # return db_url
    return 'postgres://opbwfdtemkxevm:438172d0e189438e14c08e9e03f0c9ba3dc0bce34f062e09b2be18bfea1ddd16@ec2-50-19-86-139.compute-1.amazonaws.com:5432/de1rqe4l2g1tje'


def get_db_engine(mode='prod'):
    if mode == 'prod':
        db_url = get_db_url_prod()
    else:
        db_url = 'sqlite:///heatmap.db'
    return sqlalchemy.create_engine(db_url)


def attacks_to_string(attacks):
    return reduce(lambda x, y: str(x) + '-' + str(y), attacks)


def generate_output_filename(team, player, attacks, kills, user_id):
    output_folder = 'static/images/output/%s/' % (str(user_id))
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    attacks = attacks_to_string(attacks)
    filename = 'output_team_%d_player_%d_attacks_%s_kills_%s.png' % (team, player, attacks, kills)

    return output_folder + filename


def generate_caption(team, player, attacks, kills):
    engine = get_db_engine()
    attacks_str = attacks_to_string(attacks)
    team_name = datastore.get_teamname_by_number(engine, team)
    top_caption = '%s #%d' % (team_name, player)
    bottom_caption = 'Attacks: %s' % attacks_str
    if kills:
        bottom_caption += ' (Only Kills)'
    return top_caption, bottom_caption


class Color():
    white = 255, 240, 200
    red = 255, 0, 0
    green = 0, 255, 0
    yellow = 255, 255, 0
    black = 20, 20, 40
