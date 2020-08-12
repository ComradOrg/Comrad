import os,time
from pathlib import Path
from models import *
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
from twisted.internet import defer
from twisted.internet.defer import ensureDeferred
from twisted.logger import Logger
log = Logger()

from klein import Klein

import json
jsonify = json.dumps

# Start server

app = Klein()
app.config = {}
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'Bring out number weight & measure in a year of dearth'
# socketio = SocketIO(app)
app.config['UPLOAD_DIR'] = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


## errors


@app.route('/')
def home(request): return jsonify({'error':'404 go home friend'})


# Api Functions

def read_request_json(request):
    json_str = str(request.content.read().decode('utf-8'))
    # print('json_str',type(json_str),json_str)
    return json.loads(json_str)

def get_person(name):
    print('sleeping...')
    time.sleep(10)
    person = Person.nodes.get_or_none(name=name)
    print('returning?')
    return person

## LOGIN
@app.route('/api/login',methods=['POST'])
def login(request):
    data=read_request_json(request)
    print('data',data)

    
    
    name=data.get('name','')
    passkey=data.get('passkey','')
    if not (name and passkey):
        request.setResponseCode(400)
        return jsonify({'error':'Login failed'})

    # print('sleeping...')
    # time.sleep(10)
    # person = yield Person.nodes.get_or_none(name=name)
    # print('sleeping...?')
    person = get_person(name)

    if person is None:
        request.setResponseCode(401)
        return jsonify({'error':'User exists'})

    real_passkey = person.passkey
    if not check_password_hash(real_passkey, passkey):
        request.setResponseCode(401)
        return jsonify({'error':'Login failed'})

    request.setResponseCode(200)
    return jsonify({'success':'Login success'})

@app.route('/api/register',methods=['POST'])
def register(request):
    data=read_request_json(request)
    
    name=data.get('name','')
    passkey=data.get('passkey','')

    if not (name and passkey):
        request.setResponseCode(400)
        return {'error':'Register failed'},status.HTTP_400_BAD_REQUEST

    person = Person.nodes.get_or_none(name=name)
    if person is not None:
        request.setResponseCode(401)
        return {'error':'User exists'}

    passkey = generate_password_hash(passkey)

    person = Person(name=name,passkey=passkey).save()
    
    print('REGISTERED!',data)
    return {'success':'Account created', 'username':name},status.HTTP_200_OK






## CREATE

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload',methods=['POST'])
def upload(request):
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
def post(request,post_id=None):

    if request.method == 'POST':
        # get data
        data=read_request_json(request)
        print('POST /api/post:',data)

        # make post
        post = Post(content=data.get('content','')).save()

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
def download(request, prefix, filename):
    filedir = os.path.join(app.config['UPLOAD_DIR'], prefix)
    print(filedir, filename)
    return send_from_directory(filedir, filename)

### READ


@app.route('/api/followers/<name>')
def get_followers(request, name=None):
    person = Person.match(G, name).first()
    data = [p.data for p in person.followers]
    return jsonify(data)

@app.route('/api/followers/<name>')
def get_follows(request, name=None):
    person = Person.match(G, name).first()
    data = [p.data for p in person.follows]
    return jsonify(data)


@app.route('/api/posts')
@app.route('/api/posts/<name>')
def get_posts(request, name=None):
    if name:
        person = Person.nodes.get_or_none(name=name)
        data = [p.data for p in person.wrote.all] if person is not None else []
    else:
        data = [p.data for p in Post.nodes.all()]
        # print(data)

    return jsonify({'posts':data})

@app.route('/api/post/<int:id>')
def get_post(request, id=None):
    post = Post.match(G, int(id)).first()
    data = post.data
    return jsonify(data)



if __name__=='__main__':
    app.run(host='0.0.0.0', port=5555)
    # socketio.run(app, host='0.0.0.0', port=5000)
