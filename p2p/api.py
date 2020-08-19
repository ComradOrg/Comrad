import os,time,sys,logging
from pathlib import Path
import asyncio
# handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger = logging.getLogger(__file__)
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)
sys.path.append('../p2p')
# logger.info(os.getcwd(), sys.path)


try:
    from .crypto import *
    from .p2p import *
    from .kad import *
except ModuleNotFoundError:
    from crypto import *
    from p2p import *
    from kad import KadServer
from pathlib import Path
from functools import partial

# works better with tor?
import json
jsonify = json.dumps

# Start server

DEBUG = True
UPLOAD_DIR = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# PORT_SPEAK = 8468
PORT_LISTEN = 5639

# Api Functions
from threading import Thread

def start_selfless_thread():
    async def _go():
        loop=asyncio.get_event_loop()
        return boot_selfless_node(port=PORT_SPEAK, loop=loop)
    return asyncio.run(_go())

async def _getdb(self=None,port=PORT_LISTEN):
    
    if self: self.log('starting server..')

    import os
    self.log(os.getcwd())
    node = KadServer(storage=HalfForgetfulStorage(fn='../p2p/cache.sqlite'))

    if self: self.log('listening..')
    await node.listen(port)

    if self: self.log('bootstrapping server..')
    await node.bootstrap(NODES_PRIME)
    return node

def logg(x):
    print(x)

class Api(object):
    def __init__(self,app = None):
        self.app=app
        self.app_storage = self.app.store if app else {}
        self.log = self.app.log if app else logg
        
        # self.log('starting selfless daemon...')
        # self.selfless = Thread(target=start_selfless_thread)
        # self.selfless.daemon = True
        # self.selfless.start()

        # connect?
        #self._node=self.connect()
        pass

    async def connect_forever(self):
        try:
            i = 0
            self._node = await self.connect()
            while True:
                self.log(f'Node status (minute {i}): {self._node}')

                    # # get some sleep
                    # if self.root.ids.btn1.state != 'down' and i >= 2:
                    #     i = 0
                    #     self.log('Yawn, getting tired. Going to sleep')
                    #     self.root.ids.btn1.trigger_action()

                #i += 1
                await asyncio.sleep(60)
                # pass
        except asyncio.CancelledError as e:
            self.log('Wasting time was canceled', e)
        finally:
            # when canceled, print that it finished
            self.log('Done wasting time')

    @property
    async def node(self):
        if not hasattr(self,'_node'):
            self._node=await self.connect()
        return self._node

    async def connect(self,port=PORT_LISTEN):
        self.log('connecting...')
        return await _getdb(self,port)


    async def get(self,key_or_keys):

        async def _get():
            # self.log('async _get()',self.node)
            #node=await _getdb(self)
            node=await self.node
            
            if type(key_or_keys) in {list,tuple,dict}:
                keys = key_or_keys
                res = await asyncio.gather(*[node.get(key) for key in keys])
                #log('RES?',res)
            else:
                key = key_or_keys
                res = await node.get(key)

            #node.stop()
            return res
            
        return await _get()
    
    async def set(self,key_or_keys,value_or_values):
        async def _set():
            # self.log('async _set()',self.node)
            # node=self.node
            #node=await _getdb(self)
            node=await self.node
            
            if type(key_or_keys) in {list,tuple,dict}:
                keys = key_or_keys
                values = value_or_values
                assert len(keys)==len(values)
                res = await asyncio.gather(*[node.set(key,value) for key,value in zip(keys,values)])
                # self.log('RES?',res)
            else:
                key = key_or_keys
                value = value_or_values
                res = await node.set(key,value)

            #node.stop()
            return res

        return await _set()

    async def get_json(self,key_or_keys):
        res = await self.get(key_or_keys)
        self.log('GET_JSON',res)
        if type(res)==list:
            # self.log('is a list!',json.loads(res[0]))
            return [None if x is None else json.loads(x) for x in res]
        else:
            #log('RES!!!',res)
            return None if res is None else json.loads(res)



    async def set_json(self,key,value):
        value_json = jsonify(value)
        # self.log('OH NO!',sys.getsizeof(value_json))
        return await self.set(key,value_json)

    async def has(self,key):
        val=await self.get(key)
        return val is not None


    ## PERSONS
    async def get_person(self,username):
        return await self.get_json('/person/'+username)

    async def set_person(self,username,public_key):
        pem_public_key = save_public_key(public_key,return_instead=True)
        obj = {'name':username, 'public_key':pem_public_key.decode()}
        await self.set_json('/person/'+username,obj)





    ## Register
    async def register(self,name,passkey):
        if not (name and passkey): return {'error':'Name and password needed'}
        person = await self.get_person(name)
        if person is not None: return {'error':'Username already exists'}

        private_key,public_key = new_keys(password=passkey,save=False)
        pem_private_key = save_private_key(private_key,password=passkey,return_instead=True)
        pem_public_key = save_public_key(public_key,return_instead=True)

        self.app_storage.put('_keys',
                            private=str(pem_private_key.decode()),
                            public=str(pem_public_key.decode())) #(private_key,password=passkey)
        await self.set_person(name,public_key)
        

        return {'success':'Account created', 'username':name} 

    def load_private_key(self,password):
        if not self.app_storage.exists('_keys'): return None
        pem_private_key=self.app_storage.get('_keys').get('private')
        try:
            return {'success':load_private_key(pem_private_key.encode(),password)}
        except ValueError as e:
            self.log('!!',e)
        return {'error':'Incorrect password'}



    ## LOGIN
    async def login(self,name,passkey):
        # verify input
        if not (name and passkey):
            return {'error':'Name and password required'}

        # try to load private key
        private_key_dat = self.load_private_key(passkey)
        if 'error' in private_key_dat:
            return {'error':private_key_dat['error']}
        if not 'success' in private_key_dat:
            return {'error':'Incorrect password?'}
        private_key = private_key_dat['success']

        # see if user exists
        person = await self.get_person(name)
        self.log(person)
        if person is None:
            return {'error':'Login failed'}

        # verify keys
        person_public_key_pem = person['public_key']
        public_key = load_public_key(person_public_key_pem.encode())
        real_public_key = private_key.public_key()

        #log('PUBLIC',public_key.public_numbers())
        #log('REAL PUBLIC',real_public_key.public_numbers())

        if public_key.public_numbers() != real_public_key.public_numbers():
            return {'error':'Keys do not match!'}
        return {'success':'Login successful', 'username':name}

    async def append_json(self,key,data):
        sofar=await self.get_json(key)
        if sofar is None: sofar = []
        new=sofar + ([data] if type(data)!=list else data)
        if await self.set_json(key, new):
            return {'success':'Length increased to %s' % len(new)}
        return {'error':'Could not append json'}

    async def upload(self,filename,file_id=None, uri='/file/',uri_part='/part/'):
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
            
            self.log('part!:',sys.getsizeof(part))
            #self.set(part_key,part)

            if len(parts)>=buffer_size:
                self.log('setting...')
                await self.set(part_keys,parts)
                part_keys=[]
                PARTS+=parts
                parts=[]

        # set all parts    
        #self.set(part_keys,PARTS)
        self.log('# parts:',len(PARTS))
        if parts and part_keys: await self.set(part_keys, parts)

        # how many parts?
        self.log('# pieces!',len(part_ids))

        file_store = {'ext':os.path.splitext(filename)[-1][1:], 'parts':part_ids}
        self.log('FILE STORE??',file_store)
        await self.set_json(uri+file_id,file_store)
        
        # file_store['data'].seek(0)
        file_store['id']=file_id
        return file_store

    async def download(self,file_id):
        file_store = await self.get_json('/file/'+file_id)
        if file_store is None: return

        self.log('file_store!?',file_store)
        keys = ['/part/'+x for x in file_store['parts']]
        pieces = await self.get(keys)
        file_store['parts_data']=pieces
        return file_store


    async def post(self,data):
        post_id=get_random_id()
        res = await self.set_json('/post/'+post_id, data)
        self.log('Api.post() got data back from set_json():',res)

        # ## add to channels
        await self.append_json('/posts/channel/earth', post_id)
        
        # ## add to user
        un=data.get('author')
        if un: await self.append_json('/posts/author/'+un, post_id)

        if res:
            return {'success':'Posted! %s' % post_id, 'post_id':post_id}
        return {'error':'Post failed'}

    async def get_post(self,post_id):
        return self.get_json('/post/'+post_id)

    async def get_posts(self,uri='/channel/earth'):
        index = await self.get_json('/posts'+uri)
        
        if index is None: return []
        data = self.get_json(['/post/'+x for x in index])
        
        return await data




## func

def bytes_from_file(filename,chunksize=8192):
    with open(filename, 'rb') as f:
        while True:
            piece = f.read(chunksize)  
            if not piece:
                break
            yield piece

def get_random_id():
    import uuid
    return uuid.uuid4().hex







def test_api():
    api = Api()
    # api.set(['a','b','c'],[1,2,3])
    api.set_json('whattttt',{'aaaaa':12222})

def test_basic():
    import asyncio
    from kademlia.network import Server

    #api = Api()
    
    # not working!
    #api.set_json('my key',{'a':'value'})

    async def run():
        # Create a node and start listening on port 5678
        node = Server()
        await node.listen(5678)

        # Bootstrap the node by connecting to other known nodes, in this case
        # replace 123.123.123.123 with the IP of another node and optionally
        # give as many ip/port combos as you can for other nodes.
        await node.bootstrap(NODES_PRIME)

        # set a value for the key "my-key" on the network
        await node.set("my-key", "my awesome value")

        # get the value associated with "my-key" from the network
        result = await node.get("my-key")

        print(result)
        return result

    res = asyncio.run(run())
    print('res = ',res)
    # res = asyncio.run(node.set(key,value))
    # print(res)

def test_provided_eg():
    import asyncio
    from kademlia.network import Server

    async def run():
        # Create a node and start listening on port 5678
        node = Server()
        await node.listen(5678)

        # Bootstrap the node by connecting to other known nodes, in this case
        # replace 123.123.123.123 with the IP of another node and optionally
        # give as many ip/port combos as you can for other nodes.
        await node.bootstrap(NODES_PRIME)

        # set a value for the key "my-key" on the network
        await node.set("my-key", "my awesome value")

        # get the value associated with "my-key" from the network
        result = await node.get("my-key")

        print(result)

    asyncio.run(run())


if __name__=='__main__':
    test_api()