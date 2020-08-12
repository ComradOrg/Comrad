import flask,os
from flask import request, jsonify, send_from_directory
from pathlib import Path
from models import *
from flask_api import FlaskAPI, status, exceptions
from werkzeug.security import generate_password_hash,check_password_hash
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename


# works better with tor?
import json
jsonify = json.dumps
jsonify = str

# Start server

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['UPLOAD_DIR'] = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/')
def home(): return {'error':'404 go home friend'}


# Api Functions

## LOGIN
@app.route('/api/login',methods=['POST'])
def login():
    data=request.json
    
    name=data.get('name','')
    passkey=data.get('passkey','')
    if not (name and passkey):
        return {'error':'Login failed'},status.HTTP_400_BAD_REQUEST

    persons = list(Person.match(G,name))
    if not persons:
        return {'error':'Login failed'},status.HTTP_401_UNAUTHORIZED

    person = persons[0]
    real_passkey = person.passkey
    if not check_password_hash(real_passkey, passkey):
        return {'error':'Login failed'},status.HTTP_401_UNAUTHORIZED

    return {'success':'Login success'},status.HTTP_200_OK

@app.route('/api/register',methods=['POST'])
def register():
    data=request.json
    
    name=data.get('name','')
    passkey=data.get('passkey','')

    if not (name and passkey):
        return {'error':'Register failed'},status.HTTP_400_BAD_REQUEST

    person = list(Person.match(G,name))
    if person:
        return {'error':'User exists'},status.HTTP_401_UNAUTHORIZED

    passkey = generate_password_hash(passkey)

    person = Person()
    person.name = name
    person.passkey = passkey

    G.push(person)

    print('REGISTERED!',data)
    return {'success':'Account created', 'username':name, 'passkey':passkey},status.HTTP_200_OK






## CREATE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_random_filename(filename):
    import uuid
    fn=uuid.uuid4().hex
    return (fn[:3],fn[3:]+os.path.splitext(filename)[-1])

@app.route('/api/upload',methods=['POST'])
def upload_file():
    files = request.files
    # check if the post request has the file part
    if 'file' not in request.files:
        return {'error':'No file found'},status.HTTP_204_NO_CONTENT
    
    file = request.files['file']
    
    # if user does not select file, browser also
    # submit an empty part without filename
    print('filename!',file.filename)
    if file.filename == '':
        return {'error':'No filename'},status.HTTP_206_PARTIAL_CONTENT
    
    if file and allowed_file(file.filename):
        print('uploading file...')
        prefix,filename = get_random_filename(file.filename) #secure_filename(file.filename)
        #odir = os.path.join(app.config['UPLOAD_DIR'], os.path.dirname(filename))
        #if not os.path.exists(odir):
        folder = os.path.join(app.config['UPLOAD_DIR'], prefix)
        if not os.path.exists(folder): os.mkdir(folder)
        file.save(os.path.join(folder, filename))
        #return redirect(url_for('uploaded_file', filename=filename))
        return {'filename':prefix+'/'+filename}, status.HTTP_200_OK

    return {'error':'Upload failed'},status.HTTP_406_NOT_ACCEPTABLE


@app.route('/api/post',methods=['POST'])
@app.route('/api/post/<int:post_id>',methods=['GET'])
def post(post_id=None):

    if request.method == 'POST':
        # get data
        data=request.json
        print('POST /api/post:',data)

        # make post
        post = Post()
        post.content = data.get('content','')
        post.img_src = data.get('img_src','')
        G.push(post)

        # attach to author
        username=data.get('username','')
        author = Person.match(G, username).first()
        print('author?', author)
        author.posts.add(post)
        # post.author.add(author)
        G.push(author)

        # return
        post_id=str(post.__ogm__.node.identity)
        print('created new post!',post_id)
        return {'post_id':post_id},status.HTTP_200_OK

    print('got post id!',post_id)
    posts = list(Post.match(G,post_id))
    if not posts:
        return {},status.HTTP_204_NO_CONTENT
    
    post=posts[0]
    print(post.data)
    return post.data,status.HTTP_200_OK

@app.route('/api/download/<prefix>/<filename>',methods=['GET'])
def download(prefix, filename):
    filedir = os.path.join(app.config['UPLOAD_DIR'], prefix)
    print(filedir, filename)
    return send_from_directory(filedir, filename)

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


@app.route('/api/posts')
@app.route('/api/posts/<name>')
def get_posts(name=None):
    if name:
        person = Person.match(G, name).first()
        data = [p.data for p in person.posts]
    else:
        # data=[]
        # def handle_row(row):
        #     node = row[0]
        #     data+=[node.data]  # do something with `node` here

        # G.match
        # G.cypher.execute("START z=node(*) RETURN z", row_handler=handle_row)
        matcher = NodeMatcher(G)
        posts = matcher.match('Post')
        # posts = Post.match(G).where("_.content = '*'")
        def to_data(post):
            d=dict(post)
            d['id']=post.identity
            return d

        data = [to_data(post) for post in posts]
        # print(data)

    return jsonify(data)

@app.route('/api/post/<int:id>')
def get_post(id=None):
    post = Post.match(G, int(id)).first()
    data = post.data
    return jsonify(data)





app.run(host='0.0.0.0', port=5555)