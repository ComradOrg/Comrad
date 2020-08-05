import flask,os
from flask import request, jsonify
from pathlib import Path
from models import *
from flask_api import FlaskAPI, status, exceptions


# Start server

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def home(): return '404 go home friend'


# Api Functions


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