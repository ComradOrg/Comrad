import os,time,sys,logging
from pathlib import Path
import asyncio,time
# handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger = logging.getLogger(__file__)
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)
sys.path.append('../p2p')
# logger.info(os.getcwd(), sys.path)
BSEP=b'||||'

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

                i += 1
                await asyncio.sleep(60)
                # pass
        except asyncio.CancelledError as e:
            self.log('P2P node cancelled', e)
        finally:
            # when canceled, print that it finished
            self.log('P2P node shutting down')

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
                res = await asyncio.gather(*[self.unpack_well_documented_val(await node.get(key)) for key in keys])
                #log('RES?',res)
            else:
                key = key_or_keys
                res = await self.unpack_well_documented_val(await node.get(key))

            #node.stop()
            return res
            
        return await _get()

    def well_documented_val(self,val,sep=BSEP,do_encrypt=True,receiver_pubkey=None):
        """
        What do we want to store with
        
        1) Timestamp
        2) Value
        3) Public key of author
        4) Signature of value by author
        """
        import time
        timestamp=time.time()
        #self.log('timestamp =',timestamp)
        
        if type(val)!=bytes:
            value = str(val)
            try:
                value_bytes = value.encode('utf-8')
            except UnicodeDecodeError:
                value_bytes = value.encode('ascii')
        else:
            value_bytes=val


        # encrypt?
        if not receiver_pubkey:
            receiver_pubkey=self.public_key_global
        # self.log('value while unencrypted =',value_bytes)
        
        # value_bytes = encrypt_msg(value_bytes, self.public_key_global)

        # self.log(f"""encrypting
        # val = {value_bytes}
        # sender_privkey = {self.private_key}
        # receiver_pubkey = {receiver_pubkey}
        # """)

        res = encrypt(value_bytes, self.private_key, receiver_pubkey)
        

        #aes_ciphertext, encry_aes_key, hmac, hmac_signature, iv, metadata
        
        # self.log('value while encrypted =  ',res)
        # stop
        aes_ciphertext, encry_aes_key, iv = res
        #self.log('value =',value)
        
        pem_public_key = serialize_pubkey(receiver_pubkey)

        #self.log('pem_public_key =',pem_public_key)
        # stop
        # self.log('aes_ciphertext = ',aes_ciphertext,type(aes_ciphertext))

        signature = sign(aes_ciphertext, self.private_key)
        # self.log('signature =',signature)

        ## Verify!
        authentic = verify_signature(signature, aes_ciphertext, self.public_key)
        # self.log('message is authentic for set??',authentic)

        # value_bytes_ascii = ''.join([chr(x) for x in value_bytes])

        # jsond = {'time':timestamp, 'val':value_bytes_ascii, 'pub':pem_public_key, 'sign':signature}
        # jsonstr=jsonify(jsond)

        time_b=str(timestamp).encode()
        val_encr = base64.b64encode(aes_ciphertext)
        val_encr_key = base64.b64encode(encry_aes_key)
        sender_pubkey_b = serialize_pubkey(self.public_key)
        receiver_pubkey_b = serialize_pubkey(receiver_pubkey)
        signature = signature

        WDV = sep.join([
            time_b,
            val_encr,
            val_encr_key,
            iv,
            receiver_pubkey_b,
            sender_pubkey_b,
            signature
        ])

        # self.log('well_documented_val() =',WDV)
        return WDV

    async def unpack_well_documented_val(self,WDV,sep=BSEP,private_key=None):
        # self.log('WDV???',WDV)
        if WDV is None: return WDV
        #WDV=[base64.b64decode(x) for x in WDV.split(sep)]
        WDV=WDV.split(sep)
        # self.log('WDV NEW:',WDV)
        
        time_b,val_encr,val_encr_key,iv,to_pub_b,from_pub_b,signature = WDV #.split(sep)
        to_pub = load_pubkey(to_pub_b)
        from_pub = load_pubkey(from_pub_b)
        
        # verify
        
        val_encr_decode = base64.b64decode(val_encr)
        authentic = verify_signature(signature,val_encr_decode,from_pub)
        # self.log('message is authentic for GET?',authentic,signature,val_encr)

        if not authentic: 
            self.log('inauthentic message!')
            return {}

        # decrypt
        # self.log('val before decryption = ',val_encr)
        if private_key is None:
            private_key=self.private_key_global
        
        val_encr = base64.b64decode(val_encr)
        val_encr_key = base64.b64decode(val_encr_key)
        # self.log(f"""decrypting
        # val_encr = {val_encr}
        # val_encr_key = {val_encr_key}
        # iv = {iv}
        # private_key = {private_key}
        # """)
        
        # try to decrypt
        val=None
        for privkey,pubkey in self.keys:
            try:
                val = decrypt(val_encr, val_encr_key, iv, privkey)
            except ValueError:
                pass
        # self.log('val after decryption = ',val)

        # time=float(time.decode())
        #val=val.decode()
        # return time,val,pub,sign
        WDV={
            'time':float(time_b.decode()),
            'val':val,
            'to':to_pub,
            'from':from_pub,
            'sign':signature
        }

        # self.log('GOT WDV:',WDV)
        return WDV
        
        
         #,signature

    
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
                res = await asyncio.gather(*[node.set(key,self.well_documented_val(value)) for key,value in zip(keys,values)])
                # self.log('RES?',res)
            else:
                key = key_or_keys
                value = value_or_values
                res = await node.set(key,self.well_documented_val(value))

            #node.stop()
            return res

        return await _set()

    async def get_json(self,key_or_keys):
        res = await self.get(key_or_keys)
        self.log('get_json() got',res)
        if res is None: return res
        
        def jsonize(entry):
            if not 'val' in entry: return entry
            val=entry['val']
            dat=json.loads(val.decode()) if val else val
            entry['val']=dat
            return entry

        if type(res)==list:
            jsonl=[jsonize(entry) for entry in res]
            return jsonl
        else:
            entry = res
            return jsonize(entry)


    async def set_json(self,key,value):
        value_json = jsonify(value)
        # self.log('OH NO!',sys.getsizeof(value_json))
        return await self.set(key,value_json)

    async def has(self,key):
        val=await self.get(key)
        return val is not None


    ## PERSONS
    async def get_person(self,username):
        return await self.get_val('/person/'+username)

    async def set_person(self,username,pem_public_key):
        # pem_public_key = save_public_key(public_key,return_instead=True)
        obj = {'name':username, 'public_key':pem_public_key}
        await self.set_json('/person/'+username,obj)





    ## Register
    async def register(self,name,passkey):
        if not (name and passkey): return {'error':'Name and password needed'}
        person = await self.get_person(name)
        if person is not None: return {'error':'Username already exists'}

        self._private_key = private_key = generate_rsa_key()
        # self._public_key = public_key = self.private_key.public_key()
        pem_private_key = serialize_privkey(self.private_key, password=passkey)# save_private_key(private_key,password=passkey,return_instead=True)
        #pem_public_key = save_public_key(public_key,return_instead=True)
        pem_public_key = serialize_pubkey(self.public_key)

        await self.set_person(name,pem_public_key.decode())
        

        self.app_storage.put('_keys',
                            private=pem_private_key.decode(),
                            public=pem_public_key.decode()) #(private_key,password=passkey)
        return {'success':'Account created', 'username':name} 


    

    def load_private_key(self,password):
        if not self.app_storage.exists('_keys'): return {'error':'No login keys present on this device'}
        pem_private_key=self.app_storage.get('_keys').get('private')
        self.log('my private key ====',pem_private_key)
        try:
            return {'success':load_privkey(pem_private_key,password)}
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
        self._private_key = private_key = private_key_dat['success']

        # see if user exists
        person = await self.get_person(name)
        self.log(person)
        if person is None:
            return {'error':'Login failed'}

        # verify keys
        self.log('got person =',person)
        person_public_key_pem = person['public_key']
        public_key = load_pubkey(person_public_key_pem) #load_public_key(person_public_key_pem.encode())
        self._public_key = real_public_key = private_key.public_key()

        #log('PUBLIC',public_key.public_numbers())
        #log('REAL PUBLIC',real_public_key.public_numbers())

        if public_key.public_numbers() != real_public_key.public_numbers():
            return {'error':'Keys do not match!'}
        return {'success':'Login successful', 'username':name}

    @property
    def public_key(self):
        if not hasattr(self,'_public_key'):
            if not hasattr(self,'_private_key'):
                self.app.root.change_screen('login')
            else:
                self._public_key=self.private_key.public_key()
        return self._public_key

    @property
    def private_key(self):
        if not hasattr(self,'_private_key'):
            self.app.root.change_screen('login')
        return self._private_key

    @property
    def public_key_global(self):
        if not hasattr(self,'_public_key_global'):
            try:
                pem=self.app.store_global.get('_keys').get('public',None)
                self.log('PEM GLOBAL = ',pem)
                self._public_key_global=load_pubkey(pem.encode())
                self.log('PUBKEYGLOBAL =',self._public_key_global)
                return self._public_key_global
            except ValueError as e:        
                self.log('!!',e)
        else:
            return self._public_key_global
        
    @property
    def private_key_global(self):
        if not hasattr(self,'_private_key_global'):
            try:
                pem=self.app.store_global.get('_keys').get('private',None)
                #self.log('PEM PRIVATE GLOBAL',pem)
                self._private_key_global=load_privkey(pem.encode())
                return self._private_key_global
            except ValueError as e:
                self.log('!!',e)
        else:
            return self._private_key_global
        
    @property
    def keys(self):
        keys= [(self.private_key_global,self.public_key_global)]
        if hasattr(self,'_private_key') and hasattr(self,'_public_key'):
            keys+=[(self.private_key,self.public_key)]
        return keys


    async def append_json(self,key,data):
        sofar=await self.get_val(key)
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
        for part in bytes_from_file(filename,chunksize=1024*4):
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
        if parts and part_keys:
            await self.set(part_keys, parts)

        # how many parts?
        self.log('# pieces!',len(part_ids))

        file_store = {'ext':os.path.splitext(filename)[-1][1:], 'parts':part_ids}
        self.log('FILE STORE??',file_store)
        await self.set_json(uri+file_id,file_store)
        
        # file_store['data'].seek(0)
        file_store['id']=file_id
        return file_store

    async def download(self,file_id):
        self.log('file_id =',file_id)
        file_store = await self.get_val('/file/'+file_id)
        self.log('file_store =',file_store)
        if file_store is None: return

        self.log('file_store!?',file_store)
        keys = ['/part/'+x for x in file_store['parts']]
        time,pieces,pub,sign = await self.get(keys)
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

    async def get_val(self,uri):
        res=await self.get_json(uri)
        self.log('get_val() got',res)
        if res is None:
            return res
        elif type(res) == dict:
            return res.get('val',None)
        elif type(res) == list:
            return [x.get('val',None) for x in res]
        return None

    async def get_post(self,post_id):
        return await self.get_val(post_id)

    async def get_posts(self,uri='/channel/earth'):
        index = await self.get_val('/posts'+uri)
        self.log('got index?',index)
        
        if index is None: return []
        data = self.get_val(['/post/'+x for x in index])
        
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