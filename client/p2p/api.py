
# import flask,os,time
# from flask import request, jsonify, send_from_directory
# from pathlib import Path
# from models import *
# from flask_api import FlaskAPI, status, exceptions
# from werkzeug.security import generate_password_hash,check_password_hash
# from flask import Flask, flash, request, redirect, url_for
# from werkzeug.utils import secure_filename
import os,time
from pathlib import Path
from flask_api import status
from .p2p import connect
import asyncio

# works better with tor?
import json
jsonify = json.dumps

# Start server

DEBUG = True
UPLOAD_DIR = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Api Functions

NODE = connect()


## LOGIN
def login(data):
    name=data.get('name','')
    passkey=data.get('passkey','')
    if not (name and passkey):
        return {'error':'Login failed'},status.HTTP_400_BAD_REQUEST

    person = Person.nodes.get_or_none(name=name)
    if person is None:
        return {'error':'User already exists'},status.HTTP_401_UNAUTHORIZED

    real_passkey = person.passkey
    if not check_password_hash(real_passkey, passkey):
        return {'error':'Login failed'},status.HTTP_401_UNAUTHORIZED

    return {'success':'Login success'},status.HTTP_200_OK

def get_person(username):
    async def go():
        return await NODE.get('/person/'+username)
        
    return asyncio.run(run())


def register(name,passkey):
    
    if not (name and passkey):
        return {'error':'Register failed'},status.HTTP_400_BAD_REQUEST

    
    if person is not None:
        return {'error':'User exists'},status.HTTP_401_UNAUTHORIZED

    private_key,public_key = crypto.new_keys(password=passkey)



    person = Person(name=name,passkey=passkey).save()
    
    print('REGISTERED!',data)
    return {'success':'Account created', 'username':name},status.HTTP_200_OK




"""

## CREATE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_random_filename(filename):
    import uuid
    fn=uuid.uuid4().hex
    return (fn[:3],fn[3:]+os.path.splitext(filename)[-1])

@app.route('/api/upload',methods=['POST'])
def upload():
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
        #prefix,filename = get_random_filename(file.filename) #secure_filename(file.filename)
        #odir = os.path.join(app.config['UPLOAD_DIR'], os.path.dirname(filename))
        #if not os.path.exists(odir):
        ext = os.path.splitext(file.filename)[-1]
        media = Media(ext=ext).save()
        uid = media.uid
        filename = media.filename
        prefix,fn=filename.split('/')
        
        folder = os.path.join(app.config['UPLOAD_DIR'], prefix)
        if not os.path.exists(folder): os.makedirs(folder)
        file.save(os.path.join(folder, fn))
        
        
        
        #return redirect(url_for('uploaded_file', filename=filename))
        return {'media_uid':uid, 'filename':filename}, status.HTTP_200_OK

    return {'error':'Upload failed'},status.HTTP_406_NOT_ACCEPTABLE


@app.route('/api/post',methods=['POST'])
@app.route('/api/post/<post_id>',methods=['GET'])
def post(post_id=None):

    if request.method == 'POST':
        # get data
        data=request.json
        print('POST /api/post:',data)

        # make post
        post = Post(content=data.get('content',''), timestamp=data.get('timestamp')).save()

        # attach author
        name = data.get('username')
        if name:
            author = Person.nodes.get_or_none(name=name)
            author.wrote.connect(post)
        
        # attach media
        media_uid=data.get('media_uid')
        if media_uid:
            media=Media.nodes.get_or_none(uid=media_uid)
            post.has_media.connect(media)

        

        # return
        post_id=post.uid
        print('created new post!',post_id)
        return {'post_id':post_id},status.HTTP_200_OK

    print('got post id!',post_id)
    post = Post.nodes.get_or_none(uid=post_id)
    if not post: return {},status.HTTP_204_NO_CONTENT
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
        person = Person.nodes.get_or_none(name=name)
        data = [p.data for p in person.wrote.all()] if person is not None else []
    else:
        data = [p.data for p in Post.nodes.order_by('-timestamp')]
        # print(data)

    return jsonify({'posts':data})

@app.route('/api/post/<int:id>')
def get_post(id=None):
    post = Post.match(G, int(id)).first()
    data = post.data
    return jsonify(data)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
    # socketio.run(app,host='0.0.0.0', port=5555)
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    # server = pywsgi.WSGIServer(('', 5555), app, handler_class=WebSocketHandler)
    # server.serve_forever()


"""