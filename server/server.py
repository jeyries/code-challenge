#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# server.py
import sys
import os
import os.path
import platform
import json
import yaml
import uuid
import subprocess
from functools import wraps
import getpass

### some checks

from model import ROOT

if not sys.version_info >= (3,4):
    print("Please Check your python version.")
    exit(0)

if not os.path.isfile(os.path.join(ROOT, 'config.yml')):
    print("Please setup config.")
    exit(0)

# if not os.path.isfile(os.path.join(ROOT, 'server.db')):
#     print("Please setup database.")
#     exit(0)

###

#import markdown
from flask_misaka import markdown
from flask_misaka import Misaka

import click

from flask import Flask, render_template
from flask import Markup
from flask import Response
from flask import session, redirect, url_for, escape, request, jsonify
from flask import g

from model import db, DATABASE
from model import get_without_failing
from model import read_file, write_file
from model import User, Task, Challenge, Record

### config

with open(os.path.join(ROOT, 'config.yml'), "rt") as f:
    CONFIG = yaml.load(f)

CHALLENGES = [Challenge(info) for info in CONFIG['challenges']]

###


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='%%',
        variable_end_string='%%',
        comment_start_string='<#',
        comment_end_string='#>',
    ))

app = CustomFlask(__name__, 
    static_folder="../static/dist", 
    template_folder="../static",
    instance_path=ROOT,
    instance_relative_config=True,
    )

md = Misaka()
md.init_app(app)

import chimptools
chimptools.logger = app.logger

# set the secret key.  keep this really secret:
app.secret_key = CONFIG['app']['secret_key']

##################

def connect_db():
    """Connects to the specific database."""
    db.connect()
    return db

def init_db():
    """Initializes the database."""
    db = get_db()
    db.create_tables([User, Task])
    db.save()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        db.close()
        g.sqlite_db = None


###################


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

######## controller

def user_create(email, password):
    users = User.select().where(User.email == email)
    if len(users) > 0:
        raise InvalidUsage('email already exist', status_code=410)

    user_uuid = str(uuid.uuid4())
    app.logger.info("create user %s", email)
    user = User.create(uuid=user_uuid, email=email, hashed="")
    user.password_set(password)
    user.save()

    return user

def user_populate_records(user):
    for challenge in CHALLENGES:
        record_uuid = str(uuid.uuid4())
        app.logger.info("user %s: adding record %s %s", user.email, challenge.identifier, record_uuid)
        record = Record.create( uuid = record_uuid
                            , user = user
                            , state = "available"
                            , challenge = challenge.identifier)
        record.save()

######## shell

@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo('Init the db')

    print("remove database")
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    print("connect database")
    db.connect()

    print("create tables")
    db.create_tables([User, Task, Record])

    print("close database")
    db.close()

@app.cli.command()
def stats():
    """Useful server stats."""

    users = User.select()
    print("found %d users:" % len(users))
    for user in users:
        print(user)

    tasks = Task.select()
    print("found %d tasks:" % len(tasks))
    for task in tasks:
        print(task)

@app.cli.command()
def watch():
    """Watch for any task."""
    import watch
    watch.watch()

@app.cli.group()
def user():
    pass

@app.cli.command()
@click.argument('email')
def create(email):
    """Create a user."""
    password = getpass.getpass('Password:')
    user = user_create(email, password)
    click.echo('Created user %s.' % user.email)

@app.cli.command()
@click.argument('email')
def populate(email):
    """Populate a user with some available challenges."""
    if email == 'all':
        for user in User.select():
            user_populate_records(user)
    else:
        user = User.get( User.email == email )
        user_populate_records(user)

user.add_command(create)
user.add_command(populate)


###################


def check_auth(email, password) -> User:
    """This function is called to check if a email /
    password combination is valid.
    """
    users = User.select().where( User.email == email ).limit(1)
    if len(users) > 0:
        user = users[0]
        if user.password_check(password):
            return user

    return None

def check_session() -> User:
    if not 'user_uuid' in session:
        app.logger.warning("no session found")
        return None

    users = User.select().where( User.uuid == session['user_uuid'] ).limit(1)
    if len(users) > 0:
        user = users[0]
        app.logger.debug("check_session %s found %s", session['user_uuid'], user.email)
        return user

    app.logger.warning("no user found for %s", session['user_uuid'])
    return None

def myself() -> User:
    # may throw
    return User.get( User.uuid == session['user_uuid'] )

def authenticate():
    """Sends a 401 response that enables basic auth"""
    response = """Could not verify your access level for that URL.
You have to login with proper credentials.
"""
    return Response(response=response, status=401, mimetype="text/plain", 
                    headers={'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or check_auth(auth.email, auth.password) is None:
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def requires_session(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if check_session() is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
@requires_session
def index():
    user = myself()

    codechallenge = {
      "user": user.json,
      "challenges": [x.json for x in CHALLENGES],
    }

    return render_template("index.html", 
                codechallenge=json.dumps(codechallenge, indent=4, sort_keys=True), 
                fullname=user.email)

@app.route("/solve/<identifier>")
@requires_session
def solve(identifier):
    user = myself()
    
    challenge = next((x for x in CHALLENGES if x.identifier == identifier), None)
    if challenge is None:
        raise InvalidUsage('challenge not found', status_code=404)

    records = user.records.where(Record.challenge == identifier).limit(1)
    record = records[0]
    record.start()

    codechallenge = {
      "user": user.json,
      "challenge": challenge.json,
    }

    readme = read_file(challenge.readme) 

    return render_template("solve.html", 
                codechallenge=json.dumps(codechallenge, indent=4, sort_keys=True), 
                fullname=user.email, 
                readme=readme,
                challenge=challenge)

@app.route("/join/<token>")
def join(token):
    codechallenge = {
      "token": token,
    }

    return render_template("register.html",
                codechallenge=json.dumps(codechallenge, indent=4, sort_keys=True))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = check_auth( request.form['email'], request.form['password'])
        if user is None:
            app.logger.warning('wrong login %s', request.form['email'])
            return render_template("login.html", message="wrong login.")
        session['user_uuid'] = user.uuid
        app.logger.info('login %s', user.email)
        return redirect(url_for('index'))
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    # remove the user_uuid from the session if it's there
    session.pop('user_uuid', None)
    return redirect(url_for('index'))

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

@app.route("/leaderboard.json")
def leaderboard_json():
    users = User.select().order_by(User.score.desc(), User.duration.asc(), User.email)
    rank = 1
    prev = None
    ranked = []
    for user in users:
        if prev is not None:
            if not (prev.score == user.score and prev.duration == user.duration):
                rank = 1 + len(ranked)
        prev = user
        ranked.append({
            'rank': rank,
            'uuid': user.uuid,
            'email': user.email,
            'score': user.score,
            'duration': user.duration,
            })

    response = {
        'users': ranked,
    }
    return Response(response=json.dumps(response, sort_keys=True), status=200, mimetype="application/json")

@app.route("/hello")
def hello():
    return "Hello World!"

@app.route("/info")
def info():
    lines = []
    
    users = User.select()
    lines.append("found %d users:" % len(users))
    for user in users: 
        lines.append("- %s %s" % (user.uuid, user.email))

    tasks = Task.select()
    lines.append("found %d tasks:" % len(tasks))
    for task in tasks: 
        lines.append("- %s %s %s" % (task.uuid, task.user.email, task.state))
    
    return Response(response="\n".join(lines), status=200, mimetype="text/plain")

@app.route('/user/list')
def show_user_list():
    users = User.select()
    response = [{
        'uuid': user.uuid,
        'email': user.email,
    } for user in users]
    return Response(response=json.dumps(response), status=200, mimetype="application/json")

@app.route('/user/me')
@requires_session
def show_user_me():
    user = myself()
    response = user.json
    return Response(response=json.dumps(response), status=200, mimetype="application/json")

@app.route('/user/<uuid:identifier>')
def show_user(identifier):
    user = User.get(User.uuid == identifier)
    response = user.json
    return Response(response=json.dumps(response), status=200, mimetype="application/json")

@app.route('/user/create', methods=['POST', 'GET'])
def show_user_create():
    content = request.json
    expected = CONFIG['app']['register']['token']
    if content['token'] != expected:
        app.logger.warning("wrong token for %s", content['email'])
        raise InvalidUsage('wrong token', status_code=403)
    user = user_create(content['email'], content['password'])
    response = {'result': 'OK', 'user': user.json}
    return Response(response=json.dumps(response), status=200, mimetype="application/json")

@app.route('/task/list')
def show_task_list():
    tasks = Task.select()
    response = [task.json for task in tasks]
    return Response(response=json.dumps(response), status=200, mimetype="application/json")

@app.route('/task/<uuid:identifier>')
def show_task(identifier):
    task = Task.get(Task.uuid == identifier)
    response = task.json
    return Response(response=json.dumps(response), status=200, mimetype="application/json")

@app.route('/challenge/list')
def show_challenge_list():
    response = [challenge.json for challenge in CHALLENGES]
    return Response(response=json.dumps(response), status=200, mimetype="application/json")

@app.route('/challenge/<identifier>')
def show_challenge(identifier):
    challenge = next((x for x in CHALLENGES if x.identifier == identifier), None)
    if challenge is None:
        raise InvalidUsage('challenge not found', status_code=404)
    response = challenge.json
    return Response(response=json.dumps(response), status=200, mimetype="application/json")

@app.route("/submit", methods=['POST', 'GET'])
def submit():
    user = check_session()
    if user is None:
        return Response(response="unauthorized", status=401, mimetype="text/plain")
    
    content = request.json
    app.logger.info('submit %s %s', user.email, content['language'])

    challenge = next(x for x in CHALLENGES if x.identifier == content['challenge'])

    identifier = str(uuid.uuid4())
    task = Task.create(uuid=identifier, user=user, state='reset', challenge=challenge.identifier)
    task.max = challenge.max

    write_file( task.answer, content['answer'] )

    meta = {
        "email": user.email,
        "language": content['language'],
    }

    write_file( task.meta, json.dumps(meta) )

    task.state='todo'
    task.save()

    response = {'result': 'OK', 'task': task.json}
    return Response(response=json.dumps(response), status=200, mimetype="application/json")

##################

def main():

    app.run(host='0.0.0.0',port=5000, 
        debug = True)
    

if __name__ == "__main__":
    main()
    

    
