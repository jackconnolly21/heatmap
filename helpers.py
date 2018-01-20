from flask import redirect, render_template, request, session, url_for
from functools import wraps

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

def create_user(con, user):
    """
    Create a new project into the projects table
    :param con:
    :param user:
    :return: user id
    """
    sql = ''' INSERT INTO users(username,hash,name)
              VALUES(?,?,?) '''
    cur = con.cursor()
    cur.execute(sql, user)
    return cur.lastrowid

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['dvw'])
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
