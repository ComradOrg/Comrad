import flask,os
from flask import request, jsonify
from pathlib import Path
from models import *
from flask_api import FlaskAPI, status, exceptions
from werkzeug.security import generate_password_hash,check_password_hash

# Start server

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def home(): return '404 go home friend'


# Api Functions

## LOGIN
@app.route('/api/login',methods=['POST'])
def login():
    data=request.json
    
    name=data.get('name','')
    passkey=data.get('passkey','')
    if not (name and passkey):
        return 'Login failed',status.HTTP_400_BAD_REQUEST

    persons = list(Person.match(G,name))
    if not persons:
        return 'Login failed',status.HTTP_401_UNAUTHORIZED

    person = persons[0]
    real_passkey = person.passkey
    if not check_password_hash(real_passkey, passkey):
        return 'Login failed',status.HTTP_401_UNAUTHORIZED

    return 'Login success',status.HTTP_200_OK

@app.route('/api/register',methods=['POST'])
def register():
    data=request.json
    
    name=data.get('name','')
    passkey=data.get('passkey','')

    if not (name and passkey):
        return 'Register failed',status.HTTP_400_BAD_REQUEST

    person = list(Person.match(G,name))
    if person:
        return 'User exists',status.HTTP_401_UNAUTHORIZED

    passkey = generate_password_hash(passkey)

    person = Person()
    person.name = name
    person.passkey = passkey

    G.push(person)

    print('REGISTERED!',data)
    return 'Account created',status.HTTP_200_OK






## CREATE

@app.route('/api/post',methods=['POST'])
def create_post():
    data=request.json


### READ


@app.route('/api/followers/<name>')
def get_followers(name=None):
    person = Person.match(G, name).first()
    data = [p.data for p in person.followers]
    return jsonify(data)

@app.route('/api/followers/<name>')
def get_follows(name=None):
    person = Person.match(G, name).first()
    data = [p.data for p in person.follows]
    return jsonify(data)

@app.route('/api/posts/<name>')
def get_posts(name=None):
    person = Person.match(G, name).first()
    data = [p.data for p in person.posts]
    return jsonify(data)

@app.route('/api/post/<int:id>')
def get_post(id=None):
    post = Post.match(G, int(id)).first()
    data = post.data
    return jsonify(data)





app.run(port=5555)