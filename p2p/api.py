# ### Constants
# BSEP=b'||||||||||'
# BSEP2=b'@@@@@@@@@@'
# BSEP3=b'##########'
#

# P2P_PREFIX=b'/persona/'
# P2P_PREFIX_POST=b'/msg/'
# P2P_PREFIX_INBOX=b'/inbox/'
# P2P_PREFIX_OUTBOX=b'/outbox/'

# DEBUG = True
# UPLOAD_DIR = 'uploads/'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# PORT_LISTEN = 5639
# NODE_SLEEP_FOR=1
# NODES_PRIME = [("128.232.229.63",8467)] 
LAST_N_IN_INBOX = 10


### Imports

import os,time,sys,logging
from pathlib import Path
import asyncio,time,sys
from base64 import b64encode,b64decode
sys.path.append(os.path.dirname(__file__))
import logging
import asyncio
import shelve
from collections import OrderedDict
import pickle,os
from threading import Thread
from pathlib import Path

# local imports
from persona import *
CACHE_DIR = os.path.join(os.path.expanduser('~'),'.komrade','.cache')
if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR)
MEMCACHE_FNFN=os.path.join(CACHE_DIR,'.memory')


### Logging
def logger():
    import logging
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s]\n%(message)s\n')
    handler.setFormatter(formatter)
    logger = logging.getLogger(__file__)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

LOG = None

def log(*x):
    global LOG
    if not LOG: LOG=logger().debug

    tolog=' '.join(str(_) for _ in x)
    LOG(tolog)



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

def get_random_binary_id():
    import base64
    idstr = get_random_id()
    return base64.b64encode(idstr.encode())

### Headless API

def boot_lonely_selfless_node(port=8467):
    async def go():
        api = Api(log=log, port=port)
        await api.connect_forever()
    asyncio.run(go())


class NetworkStillConnectingError(OSError): pass



async def _getdb(self=None,port=PORT_LISTEN):
    from kademlia.network import Server

    if self: 
        self.log('starting server on port %s..' % port)

    import os
    if self: self.log(os.getcwd())
    node = Server(log=self.log if self else None) #fn='../p2p/data.db',log=(self.log if self else print)))

    try:
        if self: self.log('listening on port %s...' % format(port))
        await node.listen(port)
    except OSError:
        raise NetworkStillConnectingError('Still connecting...')
        #await asyncio.sleep(3)

    if self: self.log('bootstrapping server..')
    await node.bootstrap(NODES_PRIME)

    if self: node.log = self.log
    self.log('NODE:',node)

    # if self and self.app:
        # self.app.close_dialog()

    return node

def logg(*x):
    print(*x)








class Api(object):
    def __init__(self,log=None,port=PORT_LISTEN):
        self.log = log if log is not None else logg
        self.port=port
        
        # load file-based keys
        self.load_keys()

    @property
    def app_person(self):
        return self.keys['komrade']

    async def connect_forever(self,save_every=60):
        try:
            i = 0
            self._node = await self.connect()
            while True:
                if not i%90: self.log(f'Node status (tick {i}): {self._node}')
                if i and not i%save_every: await self.flush()
                i += 1
                await asyncio.sleep(NODE_SLEEP_FOR)
                # asyncio.sleep(0)
        except (asyncio.CancelledError,KeyboardInterrupt) as e:
            self.log('P2P node cancelled', e)
            await self.flush()
        finally:
            # when canceled, print that it finished
            self.log('P2P node shutting down')
            pass
        
    @property
    async def node(self):        
        if not hasattr(self,'_node'):
            await self.connect()
            self._node.log=self.log
        return self._node

    async def connect(self):
        port=self.port
        # if self.app: self.app.open_dialog('hello?')
        self.log('connecting on port %s...' % port)
        node = await _getdb(self,port)
        self.log(f'connect() has node {node}')
        self._node = node
        return node
    

    #@property
    def load_keys(self):
        # get key names
        pub_key_names = [x.split('.')[1] for x in os.listdir(KEY_PATH_PUB) if x.count('.')==2 and x.endswith('.loc')]
        priv_key_names = [x.split('.')[1] for x in os.listdir(KEY_PATH_PRIV) if x.count('.')==2 and x.endswith('.key')]
        key_names = set(pub_key_names)|set(priv_key_names)

        self.log('get_keys() found public key names:',pub_key_names)
        self.log('get_keys() found private key names:',priv_key_names)


        # load and find all local
        self._keys = {}
        for key_name in key_names:
            self.log('key_name =',key_name)
            self._keys[key_name] = Persona(key_name,api=self,create_if_missing=False)
        
        # break into types
        self.accounts = [self._keys[name] for name in priv_key_names]
        self.contacts = [self._keys[name] for name in pub_key_names]
        
        self.log('get_keys() loaded accounts:',self.accounts)
        self.log('get_keys() loaded contacts:',self.contacts)

    @property
    def keys(self):
        if not hasattr(self,'_keys'): self.load_keys()
        return self._keys

    async def personate(self,persona_name,create_if_missing=True):
        persona = Persona(persona_name,api=self,create_if_missing=create_if_missing)
        await persona.boot()
        return persona
        # persona = self.keys[persona_name] if persona_name in self.keys else None
        # if persona is None and create_if_missing:
        #     self.keys[persona_name] = persona = Persona(persona_name, api=self, create_if_missing=create_if_missing) 
        #     res = await persona.boot()
        #     self.log('BOOT RESULT:',res)
        # return persona


    async def upload(self,filename,file_id=None, uri='/file/',uri_part='/part/'):
        import sys

        if not file_id: file_id = get_random_id()
        part_ids = []
        part_keys = []
        parts=[]
        PARTS=[]
        buffer_size=100
        for part in bytes_from_file(filename,chunksize=1024*2):
            part_id = get_random_id()
            part_ids.append(part_id)
            part_key='/part/'+part_id
            part_keys.append(part_key)
            parts.append(part)
            # PARTS.append(part)
            
            # self.log('part!:',sys.getsizeof(part))
            #self.set(part_key,part)

            if len(parts)>=buffer_size:
                # self.log('setting...')
                await self.set(part_keys,parts)
                part_keys=[]
                PARTS+=parts
                parts=[]

        # set all parts    
        #self.set(part_keys,PARTS)
        # self.log('# parts:',len(PARTS))
        if parts and part_keys:
            await self.set(part_keys, parts)

        # how many parts?
        # self.log('# pieces!',len(part_ids))

        file_store = {'ext':os.path.splitext(filename)[-1][1:], 'parts':part_ids}
        # self.log('FILE STORE??',file_store)
        await self.set_json(uri+file_id,file_store)
        
        # file_store['data'].seek(0)
        file_store['id']=file_id
        return file_store

    async def download(self,file_id):
        self.log('file_id =',file_id)
        file_store = await self.get_json_val('/file/'+file_id)
        self.log('file_store =',file_store)
        if file_store is None: return

        self.log('file_store!?',file_store)
        keys = ['/part/'+x for x in file_store['parts']]
        
        #time,pieces,pub,sign = await self.get_json_val(keys)
        pieces = await self.get_json_val(keys)
        self.log('pieces = ',pieces)
        file_store['parts_data']=pieces
        return file_store

    async def flush(self):
        #self.log('saving back to db file...')
        node = await self.node
        node.storage.dump()
        # self.log('DONE saving back to db file...')



    async def get_posts(self,uri='/inbox/world'):
        # get IDs
        post_ids = await self.get_post_ids(uri)
        
        # get posts
        posts = [self.get_post(post_id) for post_id in post_ids]
        return await asyncio.gather(*posts)
        


    ## POSTING/SENDING MSGS

    async def post(self,encrypted_payload_b64,to_person):
        # double wrap
        double_encrypted_payload = self.app_person.encrypt(encrypted_payload_b64, to_person.pubkey_b64)
        self.log('double_encrypted_payload =',double_encrypted_payload)

        post_id = get_random_binary_id() #get_random_id().encode()
        node = await self.node

        uri_post = P2P_PREFIX_POST + post_id
        res = await node.set(uri_post, double_encrypted_payload)
        self.log('result of post() =',res)

        return uri_post

    async def send(self,msg_b,from_person,to_person):
        """
        1) [Encrypted payload:]
            1) Timestamp
            2) Public key of sender
            3) Public key of recipient
            4) AES-encrypted Value
        2) [Decryption tools]
            1) AES-decryption key
            2) AES decryption IV value
        5) Signature of value by author
        """
        
        if type(msg_b)==str: msg_b=msg_b.encode()
        msg_b64=b64encode(msg_b)

        # encrypt and sign
        encrypted_payload = from_person.encrypt(msg_b64, to_person.pubkey_b64)
        signed_encrypted_payload = from_person.sign(encrypted_payload)

        # package
        time_b64 = b64encode(str(time.time()).encode())
        WDV_b64 = b64encode(BSEP.join([
            signed_encrypted_payload,
            from_person.pubkey_b64,
            from_person.name_b64,
            time_b64]))
        self.log('WDV_b64 =',WDV_b64)

        # post
        post_id = await self.post(WDV_b64, to_person)
        self.log('post_id <-',post_id)

        # add to inbox
        res = await to_person.add_to_inbox(post_id)
        self.log('add_to_inbox <-',res)

        # add to outbox?
        # pass


    async def read_inbox(self,uri_inbox=None):
        if uri_inbox is None: uri_inbox = P2P_PREFIX_INBOX+self.name.encode()
        node = await self.node
        inbox_ids = await node.get(uri_inbox)
        if inbox_ids is not None:
            inbox_ids = inbox_ids.split(BSEP)
            self.log('found inbox IDs:',inbox_ids)

            msgs_toread = [self.read_msg(msg_id) for msg_id in inbox_ids]
            msgs =  await asyncio.gather(*msgs_toread)
            self.log('read_inbox() msgs = ',msgs)
            return msgs
        return []

    async def read_outbox(self,uri_outbox=None):
        if uri_outbox is None: uri_outbox = P2P_PREFIX_OUTBOX+self.name.encode()
        return await self.read_inbox(uri_outbox)


    async def read_msg(self,msg_id):
        self.log(f'Persona.read_msg({msg_id}) ?')
        uri_msg=P2P_PREFIX_POST+msg_id
        node = await self.node
        komrade = await self.komrade
            
        res = await node.get(uri_msg)
        self.log('res = ',res)
        if res is not None:
            double_encrypted_payload_b64 = res
            single_encrypted_payload = self.decrypt(double_encrypted_payload_b64, komrade.pubkey_b64)
            self.log('GOT ENRYPTED PAYLOAD:',single_encrypted_payload)

            signed_encrypted_payload_b64,from_pubkey_b64,name_b64,time_b64 = single_encrypted_payload.split(BSEP)
            self.log('signed_encrypted_payload =',signed_encrypted_payload_b64)
            self.log('from_pubkey_b64 =',from_pubkey_b64)
            self.log('time_b64 =',time_b64)
            
            from_name = b64decode(name_b64).decode()
            self.log('from_name =',from_name)
            timestamp = b64decode(time_b64).decode()
            tmpP = Persona(from_name)
            await tmpP.boot()
            from_pubkey_b64_acc_to_name = tmpP.pubkey_b64
            assert from_pubkey_b64==from_pubkey_b64_acc_to_name

            encrypted_payload_b64 = self.verify(signed_encrypted_payload_b64, from_pubkey_b64)
            self.log('encrypted_payload_b64 =',encrypted_payload_b64)
            
            payload = self.decrypt(encrypted_payload_b64, from_pubkey_b64)
            self.log('payload =',payload)
            return {
                'success':True,
                'content':payload,
                'from_name':from_name,
                'from_pubkey_b64':from_pubkey_b64,
                'timestamp':timestamp
            }
        return {'error':'Unknown'}

    async def refresh_inboxes(self):
        uris_to_get=[]

        for persona in self.accounts:
            inbox = await persona.load_inbox(decrypt_msg_uri=True, last=LAST_N_IN_INBOX)
            for decr_msg_uri in inbox:
                uris_to_get.append(self.get_msg(decr_msg_uri))
            # uris_to_get+=inbox


        res = await asyncio.gather(*uris_to_get)
        for decr_msg_uri,encr_msg in res:
            self.memcache[decr_msg_uri]=encr_msg
        
        self.memcache_save()

    @property
    def memcache(self):
        if not hasattr(self,'_memcache'):
            self._memcache = OrderedDict()
            if os.path.exists(MEMCACHE_FNFN):
                import pickle
                try:
                    self._memcache = pickle.load(open(MEMCACHE_FNFN,'rb'))
                except EOFError:
                    pass
        return self._memcache

    def memcache_save(self):
        import pickle
        with open(MEMCACHE_FNFN,'wb') as of:
            pickle.dump(self.memcache, of)
            self.log('>> saved:',MEMCACHE_FNFN)

    async def get_msg(self,decr_msg_uri):
        self.log('get_msg()',decr_msg_uri)
        rval=self.memcache.get(decr_msg_uri)
        self.log('got <--',rval)
        if rval is not None:
            self.log('in memcache')
            encr_msg = rval
        else:
            self.log('>> downloading',decr_msg_uri,'...')
            
            node = await self.node
            encr_msg = await node.get(decr_msg_uri)
            self.log('downloaded:',encr_msg)
        
        return (decr_msg_uri,encr_msg)
        #self.memcache.

    async def see(self,decr_msg_id):
        res=await self.get(decr_msg_id)
        self.log('see() saw',res)
        return decr_msg_id



async def test1():
    api = Api()

    marx=await api.personate('marx')
    elon=await api.personate('elon')
    res = await marx.send(b'secret',to=elon)

    print(marx,elon,res)

async def test():

    api = Api()


    # message?
    marx=await api.personate('marx')
    elon=await api.personate('elon')
    res = await marx.send(b'secret',to=elon)

    res = await elon.send(b'secret back',to=marx)
    # print(marx,elon,res)

    # get overall inbox 
    meta_inbox = await api.refresh_inboxes()
    api.log('meta_inbox',meta_inbox)

    keys = api.memcache.keys()
    api.log('ALL KEYS =',keys)

    for key in keys:
        val = api.memcache.get(key)
        api.log(key,'-->',val)
        # stop

async def test_keyserver():
    api = Api()
    marx = await api.personate('marx')
    elon = await api.personate('elon')


    zuck = await api.personate('zuck')
    #marx = await api.personate(marx)
    #res = await api.get_externally_signed_pubkey('marx')
    #res = await api.get_externally_signed_pubkey('marx')
    #return res


if __name__=='__main__':
    asyncio.run(test_keyserver())