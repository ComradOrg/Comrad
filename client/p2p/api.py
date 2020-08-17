
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
import asyncio
from .crypto import *
from main import log
from .p2p import *
from pathlib import Path
from functools import partial

# works better with tor?
import json
jsonify = json.dumps

# Start server

DEBUG = True
UPLOAD_DIR = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
NODES_PRIME = [("128.232.229.63",8468), ("68.66.241.111",8468)]    
PORT_LISTEN = 8469

# Api Functions

class Api(object):
    

    def __init__(self,app_storage):
        #self.connect()
        self.app_storage = app_storage
        pass

   # def connect(self):
        #from .p2p import connect
        #self.node = connect()

    def get(self,key_or_keys):
        async def _get():
            node = Server(storage=HalfForgetfulStorage())
            await node.listen(PORT_LISTEN)
            await node.bootstrap(NODES_PRIME)

            if type(key_or_keys) in {list,tuple,dict}:
                keys = key_or_keys
                res = []
                res = await asyncio.gather(*[node.get(key) for key in keys])
                log('RES?',res)
            else:
                key = key_or_keys
                res = await node.get(key)

            return res
            
        return asyncio.run(_get())


    def get_json(self,key_or_keys):
        res = self.get(key_or_keys)
        if type(res)==list:
            return [None if x is None else json.loads(x) for x in res]
        else:
            return None if res is None else json.loads(res)

    def set(self,key_or_keys,value_or_values):
        log('hello?')
        async def _set():
            log('starting server...')
            node = Server() #storage=HalfForgetfulStorage())
            
            log('listening...')
            await node.listen(PORT_LISTEN)
            
            log('bootstrapping...')
            await node.bootstrap(NODES_PRIME)
            

            if type(key_or_keys) in {list,tuple,dict}:
                keys = key_or_keys
                values = value_or_values
                log(len(keys),len(values))
                assert len(keys)==len(values)
                res = await asyncio.gather(*[node.set(key,value) for key,value in zip(keys,values)])
                log('RES?',res)
            else:
                key = key_or_keys
                value = value_or_values
                res = await node.set(key,value)

            node.stop()
            return res
        return asyncio.run(_set(), debug=True)

    def set_json(self,key,value):
        value_json = jsonify(value)
        return self.set(key,value_json)

    def has(self,key):
        return self.get(key) is not None


    ## PERSONS
    def get_person(self,username):
        return self.get_json('/person/'+username)

    def set_person(self,username,public_key):
        pem_public_key = save_public_key(public_key,return_instead=True)
        obj = {'name':username, 'public_key':pem_public_key.decode()}
        self.set_json('/person/'+username,obj)





    ## Register
    def register(self,name,passkey):
        
        if not (name and passkey):
            error('name and passkey not set')
            return {'error':'Register failed'},status.HTTP_400_BAD_REQUEST

        person = self.get_person(name)
        if person is not None:
            log('error! person exists')
            return {'error':'Register failed'}

        private_key,public_key = new_keys(password=passkey,save=False)
        pem_private_key = save_private_key(private_key,password=passkey,return_instead=True)
        pem_public_key = save_public_key(public_key,return_instead=True)

        self.app_storage.put('_keys',
                            private=str(pem_private_key.decode()),
                            public=str(pem_public_key.decode())) #(private_key,password=passkey)
        self.set_person(name,public_key)
        

        log('success! Account created')
        return {'success':'Account created', 'username':name} 

    def load_private_key(self,password):
        if not self.app_storage.exists('_keys'): return None
        pem_private_key=self.app_storage.get('_keys').get('private')
        try:
            return load_private_key(pem_private_key.encode(),password)
        except ValueError as e:
            log('!!',e)
            return None



    ## LOGIN
    def login(self,name,passkey):
        # verify input
        if not (name and passkey):
            return {'error':'Name and password required'}

        # try to load private key
        private_key = self.load_private_key(passkey)
        if private_key is None:
            return {'error':'You have never registered on this device'}

        # see if user exists
        person = self.get_person(name)
        log(person)
        if person is None:
            return {'error':'Login failed'}

        # verify keys
        person_public_key_pem = person['public_key']
        public_key = load_public_key(person_public_key_pem.encode())
        real_public_key = private_key.public_key()

        #log('PUBLIC',public_key.public_numbers())
        #log('REAL PUBLIC',real_public_key.public_numbers())

        if public_key.public_numbers() != real_public_key.public_numbers():
            return {'error':'keys do not match!'}
        return {'success':'Login successful', 'username':name}

    def append_json(self,key,data):
        sofar=self.get_json(key)
        if sofar is None: sofar = []
        new=sofar + ([data] if type(data)!=list else data)
        if self.set_json(key, new):
            return {'success':'Length increased to %s' % len(new)}
        return {'error':'Could not append json'}

    def upload(self,filename,file_id=None, uri='/img/',uri_part='/part/'):
        import sys

        if not file_id: file_id = get_random_id()
        part_ids = []
        part_keys = []
        parts=[]
        PARTS=[]
        buffer_size=100
        for part in bytes_from_file(filename,chunksize=1024*7):
            part_id = get_random_id()
            part_ids.append(part_id)
            part_key='/part/'+part_id
            part_keys.append(part_key)
            parts.append(part)
            # PARTS.append(part)
            
            log('part!:',sys.getsizeof(part))
            #self.set(part_key,part)

            if len(parts)>=buffer_size:
                log('setting...')
                self.set(part_keys,parts)
                part_keys=[]
                PARTS+=parts
                parts=[]

        # set all parts    
        #self.set(part_keys,PARTS)
        log('# parts:',len(PARTS))
        if parts and part_keys: self.set(part_keys, parts)

        # how many parts?
        log('# pieces!',len(part_ids))

        file_store = {'ext':os.path.splitext(filename)[-1][1:], 'parts':part_ids}
        log('FILE STORE??',file_store)
        self.set_json(uri+file_id,file_store)
        
        # file_store['data'].seek(0)
        file_store['id']=file_id
        return file_store

    def post(self,data):
        post_id=get_random_id()
        res = self.set_json('/post/'+post_id, data)
        log('got data:',data)

        ## add to channels
        self.append_json('/posts/channel/earth', post_id)
        
        ## add to user
        un=data.get('author')
        if un: self.append_json('/posts/author/'+un, post_id)

        if res:
            return {'success':'Posted! %s' % post_id, 'post_id':post_id}
        return {'error':'Post failed'}

    def get_post(self,post_id):
        return self.get_json('/post/'+post_id)

    def get_posts(self,uri='/channel/earth'):
        index = self.get_json('/posts'+uri)
        if index is None: return []
        data = self.get_json(['/post/'+x for x in index])
        return data




## CREATE

def get_random_id():
    import uuid
    return uuid.uuid4().hex

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_random_filename(filename):
    import uuid
    fn=uuid.uuid4().hex
    return (fn[:3],fn[3:]+os.path.splitext(filename)[-1])


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


def download(prefix, filename):
    filedir = os.path.join(app.config['UPLOAD_DIR'], prefix)
    print(filedir, filename)
    return send_from_directory(filedir, filename)

### READ



def get_followers(name=None):
    person = Person.match(G, name).first()
    data = [p.data for p in person.followers]
    return jsonify(data)


def get_follows(name=None):
    person = Person.match(G, name).first()
    data = [p.data for p in person.follows]
    return jsonify(data)



def get_posts(name=None):
    if name:
        person = Person.nodes.get_or_none(name=name)
        data = [p.data for p in person.wrote.all()] if person is not None else []
    else:
        data = [p.data for p in Post.nodes.order_by('-timestamp')]
        # print(data)

    return jsonify({'posts':data})


def get_post(id=None):
    post = Post.match(G, int(id)).first()
    data = post.data
    return jsonify(data)




import sys
# def bytes_from_file(filename, chunksize=8192//2):
#     with open(filename, "rb") as f:
#         while True:
#             chunk = f.read(chunksize)
#             if chunk:
#                 log(type(chunk), sys.getsizeof(chunk))
#                 yield chunk
#                 #yield from chunk
#             else:
#                 break

# def bytes_from_file(filename,chunksize=8192):
#     with open(filename,'rb') as f:
#         barray = bytearray(f.read())

#     for part in barray[0:-1:chunksize]:
#         log('!?',part)
#         yield bytes(part)

def bytes_from_file(filename,chunksize=8192):
    with open(filename, 'rb') as f:
        while True:
            piece = f.read(chunksize)  
            if not piece:
                break
            yield piece

# import sys
# def bytes_from_file(path,chunksize=8000):
#     ''' Given a path, return an iterator over the file
#         that lazily loads the file.
#     '''
#     path = Path(path)
#     bufsize = get_buffer_size(path)

#     with path.open('rb') as file:
#         reader = partial(file.read1, bufsize)
#         for chunk in iter(reader, bytes()):
#             _bytes=bytearray()
#             for byte in chunk:
#                 #if _bytes is None:
#                 #    _bytes=byte
#                 #else:
#                 _bytes.append(byte)

#                 if sys.getsizeof(_bytes)>=8192:
#                     yield bytes(_bytes) #.bytes()
#                     _bytes=bytearray()
#         if _bytes:
#             yield bytes(_bytes)

# def get_buffer_size(path):
#     """ Determine optimal buffer size for reading files. """
#     st = os.stat(path)
#     try:
#         bufsize = st.st_blksize # Available on some Unix systems (like Linux)
#     except AttributeError:
#         bufsize = io.DEFAULT_BUFFER_SIZE
#     return bufsize