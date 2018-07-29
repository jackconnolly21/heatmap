import os
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_jsglue import JSGlue
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from tempfile import gettempdir
from flask_sqlalchemy import SQLAlchemy

import heat_map
from db import datastore
from helpers import *
from parser import Parser

app = Flask(__name__)
JSGlue(app)

# configure session to use filesystem (instead of signed cookies)
app.config['SESSION_FILE_DIR'] = gettempdir()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# configure app for uploads
UPLOAD_FOLDER = 'data/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# db
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

heroku = Heroku(app)

@app.route('/')
@login_required
def index():
    """Landing page for the website, contains form to generate heat map"""

    print 'Loading Index'

    user_upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']))
    upload_list = [f for f in os.listdir(user_upload_folder) if f.endswith('.dvw')]

    return render_template('index.html', result_dict={'uploads': upload_list})


@app.route("/heatmap", methods=['POST'])
@login_required
def heatmap():
    """Handles the creation of the heatmao"""

    team = int(request.form.get('teamname'))
    player = int(request.form.get('player'))
    attacks = request.form.get('attacks')
    data = request.form.get('datafiles')

    print 'Making heat map for player #%d, team #%d, attacks %s' % (player, team, attacks)

    if attacks.lower() == 'all':
        attacks = ['ALL']
    else:
        attacks = attacks.split(',')

    if request.form.get('kills'):
        only_kills = True
    else:
        only_kills = False

    files = []
    if data == 'uploads':
        data = 'uploads/%d' % session['user_id']
    folder = 'data/' + data
    for f in os.listdir(os.getcwd() + '/' + folder):
        if f.endswith('.dvw'):
            files.append(folder + '/' + f)

    locations = []
    for file_name in files:
        parser = Parser(file_name)
        locations = parser.get_attack_info(team, player, attacks, locations, only_kills)

    top_caption, bottom_caption = generate_caption(team, player, attacks, only_kills)
    output_url = generate_output_filename(team, player, attacks, only_kills, session['user_id'])
    output_dict = heat_map.draw_arcs_pillow(locations, output_url, top_caption=top_caption, bottom_caption=bottom_caption)

    result_dict = {
        'output_url': output_url,
        'width': output_dict['width'],
        'height': output_dict['height'],
    }

    print 'Rendering finished image'
    return render_template('heatmap.html', result_dict=result_dict)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Allows user to upload .dvw files to use as data"""
    print 'Loading upload page'

    if request.method == 'POST':
        if 'dvwfile' not in request.files:
            flash('No file given', 'danger')
            return render_template('upload.html')

        upload_file = request.files['dvwfile']
        # if user does not select file, browser also
        # submit a empty part without filename
        if upload_file.filename == '':
            flash('No selected file', 'danger')
            return render_template('upload.html')
        if upload_file and allowed_file(upload_file.filename):
            filename = secure_filename(upload_file.filename)
            upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']))

            if not os.path.isdir(upload_folder):
                os.makedirs(upload_folder)

            upload_file.save(os.path.join(upload_folder, filename))

            upload_dict = {'user_id': session['user_id'], 'file_key': filename}
            datastore.insert_upload_row(engine, upload_dict)

            flash('File Uploaded!', 'info')

        print 'Uploaded File'
        return redirect(url_for('upload'))
    else:
        return render_template('upload.html')


@app.route('/teams')
def teams():
    """Route to use in typeahead"""
    print 'Getting Teams'

    substring = '%' + request.args.get('t') + '%'

    team_list = datastore.get_teams_typeahead(engine, substring, limit=10)

    print 'Teams:', team_list
    return jsonify(team_list)


@app.route('/info')
@login_required
def info():
    """Load team info page"""
    print 'Loading info page'

    team_list = datastore.get_all_teams(engine)

    return render_template('info.html', rows=team_list)


@app.route('/combos')
@login_required
def combos():
    """Load info about combos"""
    print 'Loading combo info page'

    test_data_folder = os.path.join('data', 'testdata')
    base_file_name = 'CU-PENN.dvw'
    base_file_key = os.path.join(test_data_folder, base_file_name)

    parser = Parser(base_file_key)
    combo_list = parser.read_combos()

    combo_dicts = [{'combo': combo, 'name': name} for combo, (name, _) in sorted(combo_list.iteritems())]

    return render_template('combos.html', rows=combo_dicts)


@app.route('/logout')
def logout():
    """Log user out."""
    print 'Logging user out'

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log user in."""

    print 'Loading login page'

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        # ensure username was submitted
        if not request.form.get('username'):
            flash('Must type username!', 'danger')
            return render_template('login.html')

        # ensure password was submitted
        elif not request.form.get('password'):
            flash('Must type password!', 'danger')
            return render_template('login.html')

        # Query database for user
        user = datastore.get_user_by_username(engine, request.form.get('username'))

        # ensure username exists and password hash is correct
        if user is None or not check_password_hash(user['hash'], request.form.get('password')):
            flash('Invalid username/password', 'danger')
            return render_template('login.html')

        session['user_id'] = user['id']

        # redirect user to index
        flash('Logged in!', 'info')
        return redirect(url_for('index'))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register User"""
    print 'Loading register page'

    session.clear()

    if request.method == 'POST':
        # check that username was provided
        if not request.form.get('username'):
            flash('Must provide username!', 'danger')
            return render_template('register.html')
        # check that name was provided
        elif not request.form.get('firstname') or not request.form.get('lastname'):
            flash('Must provide full name!', 'danger')
            return render_template('register.html')
        # check that password was provided twice
        elif not request.form.get('password') or not request.form.get('confirmation'):
            flash('Must provide password twice!', 'danger')
            return render_template('register.html')
        # check that both passwords match
        elif not request.form.get('password') == request.form.get('confirmation'):
            flash('Passwords don\'t match!', 'danger')
            return render_template('register.html')

        user_dict = {
            'username': request.form.get('username'),
            'hash': generate_password_hash(request.form.get('password')),
            'firstname': request.form.get('firstname'),
            'lastname': request.form.get('lastname')
        }
        user_id = datastore.insert_user(engine, user_dict)

        if not user_id:
            flash('Username already taken!', 'warning')
            return render_template('register.html')

        session['user_id'] = user_id

        # redirect to index
        flash('You are registered!', 'info')
        return redirect(url_for('index'))

    else:
        return render_template('register.html')


@app.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    """Allow user to change password"""

    if request.method == 'POST':
        print 'Changing password'
        # query for user's hash of password
        pw_hash = datastore.get_user_by_user_id(engine, session['user_id'])['hash']

        # check all boxes filled, old password is correct, new and confirmation match
        if not request.form.get('old') or not check_password_hash(pw_hash, request.form.get('old')):
            flash('Incorrect old password!', 'danger')
            return render_template('password.html')
        elif not request.form.get('new') or not request.form.get('confirmation'):
            flash('Must confirm new password!', 'danger')
            return render_template('password.html')
        elif not request.form.get('new') == request.form.get('confirmation'):
            flash('New passwords don\'t match!', 'danger')
            return render_template('password.html')

        # update hash in database
        datastore.update_password_hash(engine, session['user_id'], generate_password_hash(request.form.get('new')))

        # redirect to portfolio
        flash('Password changed!', 'info')
        print 'Password changed!'
        return redirect(url_for('index'))

    else:
        print 'Loading change password page'
        return render_template('password.html')
