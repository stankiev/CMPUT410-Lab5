# Most of this code was copied from: http://flask.readthedocs.org/en/latest/tutorial/introduction/\
# Copied from https://github.com/stankiev/CMPUT410-Lab4
# code edited for CMPUT410-Lab5
#
# Edited by: Dylan Stankievech and Robert Hackman
#
#
#


import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


# create our little application
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'todo.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('TODO_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'



def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def query_db(query, args=(), one=False):
    cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']	
        if username == 'admin' and password=='password':
            session['logged_in'] = True
            flash('Successfully logged in')
            return redirect(url_for('home'))
        else:
            flash('Incorrect login')
            session['logged_in'] = False
            return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    flash('Logged out')
    return redirect(url_for('home'))

@app.route('/home', methods=['POST', 'GET'])
def home():
        db = get_db()
        cur = db.execute('select category, priority, description, id from entries order by priority desc')
        entries = cur.fetchall()
        return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into entries (category, priority, description) values (?, ?, ?)',
                 [request.form['category'], request.form['priority'], request.form['description']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('home'))

@app.route('/delete', methods=['POST'])
def delete_entry():
    delete_id = request.form['id']
    db = get_db()
    db.execute('delete from entries where id = ?', [delete_id])
    db.commit()
    flash('Entry was successfully deleted')
    return redirect(url_for('home'))
