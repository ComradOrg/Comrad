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
BSEP=b'||||||||||'
BSEP2=b'@@@@@@@@@@'
BSEP3=b'##########'
NODE_SLEEP_FOR=1
PATH_WORLD_KEY='.world.key'


try:
    from .crypto import *
    from .p2p import *
    from .kad import *
except (ModuleNotFoundError,ImportError):
    from crypto import *
    from p2p import *
    from kad import *
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


NODES_PRIME = [("128.232.229.63",8467), ("68.66.241.111",8467)] 
#68.66.224.46

from pathlib import Path
home = str(Path.home())

KEYDIR = os.path.join(home,'.komrade','.keys')
if not os.path.exists(KEYDIR): os.makedirs(KEYDIR)

KEYDIR_BUILTIN = '.'

class NetworkStillConnectingError(OSError): pass

async def _getdb(self=None,port=PORT_LISTEN):
    from kademlia.network import Server

    if self: 
        self.log('starting server..')

    import os
    if self: self.log(os.getcwd())
    node = Server(log=self.log if self else None) #fn='../p2p/data.db',log=(self.log if self else print)))

    try:
        if self: self.log('listening..')
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
    def __init__(self,user=None,log=None,app=None):
        self.log = log if log is not None else logg
        self.username = user
        self.app=app

    def private_key(self):
        if self.username:
            pass

    async def connect_forever(self,port=PORT_LISTEN,save_every=60):
        try:
            i = 0
            self._node = await self.connect(port=port)
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
        # while not hasattr(self,'_node'):
        #     self.log('[API] waiting forr connection...')
        #     await asyncio.sleep(1)
        # return self._node
        
        if not hasattr(self,'_node'):
            await self.connect()
            self._node.log=self.log
        return self._node

    async def connect(self,port=PORT_LISTEN):
        if self.app: self.app.open_dialog('hello?')
        self.log('connecting...')
        node = await _getdb(self,port)
        self.log(f'connect() has node {node}')
        self._node = node
        return node



    async def get(self,key_or_keys,decode_data=True):
        self.log(f'api.get({key_or_keys},decode_data={decode_data}) --> ...')
        async def _get():
            self.log(f'api._get({key_or_keys},decode_data={decode_data}) --> ...')
            node=await self.node
            res=None

            if type(key_or_keys) in {list,tuple,dict}:
                keys = key_or_keys
                self.log('keys is plural',keys)
                res =[]
                for key in keys:
                    val = None
                    
                    # while not val:
                    self.log('trying again...')
                    val = await node.get(key)
                    self.log('got',val)
                    #asyncio.sleep(1)

                    self.log(f'val for {key} = {val} {type(val)}')
                    if decode_data: 
                        self.log(f'api._get() decoding data {keys} -> {val} {type(val)}')
                        val = await self.decode_data(val)
                        self.log(f'api._get() got back decodied data {keys} -> {val} {type(val)}')
                    res+=[val]
                #res = await asyncio.gather(*tasks)
            else:
                key=key_or_keys
                # self.log('keys is singular',key)
                val = await node.get(key)
                if decode_data:
                    self.log(f'api._get() decoding data {key} -> {val} {type(val)}')
                    val = await self.decode_data(val)
                    self.log(f'api._get() got back decodied data {key} -> {val} {type(val)}')
                # self.log('wtf is val =',val)
                res=val
            
            # self.log('wtf is res =',res)
            
            self.log(f'_get({key_or_keys}) --> {res}')
            return res
        return await _get()

    # async def get(self,key_or_keys,decode_data=True):
    #     self.log(f'api.get({key_or_keys},decode_data={decode_data}) --> ...')
    #     async def _get():
    #         self.log(f'api._get({key_or_keys},decode_data={decode_data}) --> ...')
    #         node=await self.node
    #         res=None

    #         if type(key_or_keys) in {list,tuple,dict}:
    #             keys = key_or_keys
    #             self.log('keys is plural',keys)
    #             res =[]
    #             for key in keys:
    #                 val = None
                    
    #                 # while not val:
    #                 self.log('trying again...')
    #                 val = await node.get(key)
    #                 self.log('got',val)
    #                 asyncio.sleep(1)

    #                 self.log(f'val for {key} = {val} {type(val)}')
    #                 if decode_data: 
    #                     self.log(f'api._get() decoding data {keys} -> {val} {type(val)}')
    #                     val = await self.decode_data(val)
    #                     self.log(f'api._get() got back decodied data {keys} -> {val} {type(val)}')
    #                 res+=[val]
    #             #res = await asyncio.gather(*tasks)
    #         else:
    #             key=key_or_keys
    #             self.log('keys is singular',key)
    #             val = await node.get(key)
    #             if decode_data:
    #                 self.log(f'api._get() decoding data {key} -> {val} {type(val)}')
    #                 val = await self.decode_data(val)
    #                 self.log(f'api._get() got back decodied data {key} -> {val} {type(val)}')
    #             self.log('wtf is val =',val)
    #             res=val
            
    #         self.log('wtf is res =',res)
            
    #         self.log(f'_get({key_or_keys}) --> {res}')
    #         return res
    #     return await _get()

    def encode_data(self,val,sep=BSEP,sep2=BSEP2,do_encrypt=False,encrypt_for_pubkey=None,private_signature_key=None):
        assert type(val)==bytes
        """
        What do we want to store with
        
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
        import time
        timestamp=time.time()

        self.log(f"""api.encode_data(
            val={val},
            sep={sep},
            sep2={sep2},
            do_encrypt={do_encrypt},
            encrypt_for_pubkey={encrypt_for_pubkey},
            private_signature_key={private_signature_key})""")

        # check input
        if not encrypt_for_pubkey: 
            raise Exception('we need a receiver !!')
            # return None
        
        # convert val to bytes
        # if type(val)!=bytes: val = bytes(val,'utf-8')
        # value_bytes=base64.b64encode(val)
        value_bytes = val

        # sign
        private_signature_key = private_signature_key if private_signature_key is not None else self.private_key
        signature = sign(value_bytes, private_signature_key)
        public_sender_key = private_signature_key.public_key()
        sender_pubkey_b = serialize_pubkey(public_sender_key)

        # Verify!
        self.log(f'''encode_data().verify_signature(
            signature={signature}
            value={value_bytes}
            sender_pubkey={sender_pubkey_b}''')
        authentic = verify_signature(signature, value_bytes, public_sender_key)
        
        if not authentic:
            raise Exception('message is inauthentic for set??' +str(authentic))
            return None

        # encrypt?
        encrypt_for_pubkey_b = serialize_pubkey(encrypt_for_pubkey)
        #time_b=base64.b64encode(str(timestamp).encode('utf-8'))  #.encode()
        time_b=str(timestamp).encode('utf-8')
        msg=value_bytes

        # whole binary package
        WDV = [
            time_b,
            sender_pubkey_b,
            encrypt_for_pubkey_b,
            msg,
            signature
        ]
        payload = sep2.join(WDV)
        
        res = aes_rsa_encrypt(payload,encrypt_for_pubkey)
        if res is None:
            raise Exception('encryption result does not exist')
            return None
        payload_encr_aes, payload_encr_aes_key, payload_encr_aes_iv = res
        
        decryption_tools = sep2.join([
            payload_encr_aes_key,
            payload_encr_aes_iv
        ])

        final_packet = sep.join([
            payload_encr_aes,
            decryption_tools
        ])

        self.log('FINAL PACKET:',final_packet,type(final_packet))
        return final_packet

    

    async def decode_data(self,entire_packet_orig,sep=BSEP,private_key=None,sep2=BSEP2):
        if entire_packet_orig is None: return entire_packet_orig
        self.log(f'decode_data({entire_packet_orig})...')
        import binascii
        entire_packet = entire_packet_orig
        
        #self.log('PACKED =',entire_packet,type(entire_packet))
        
        #self.log('????',type(entire_packet))
        #self.log(entire_packet)
        
        # get data
        try:
            encrypted_payload, decryption_tools = entire_packet.split(sep) #split_binary(entire_packet, sep=sep)  #entire_packet.split(sep)
            decryption_tools=decryption_tools.split(sep2)  #split_binary(decryption_tools,sep=sep2)
        except ValueError as e:

            self.log('!! decode_data() got incorrect format:',e)
            self.log('packet =',entire_packet)
            return entire_packet_orig 
        

        ### NEW FIRST LINE: Try to decrypt!
        val=None
        key_used=None
        for keyname,privkey in self.keys.items():
            self.log(keyname,privkey,'??')
            try:
                # clicked!
                val = aes_rsa_decrypt(encrypted_payload,privkey,*decryption_tools)
                key_used=keyname
                # this must mean this was the recipient
                self.log(f'unlocked using key {keyname}!')
                break
            except ValueError as e:
                self.log(keyname,'did not work!') #,privkey,pubkey)
                pass
        if not val:
            raise Exception('Content not intended for us')
            return None

        #stop

        ### THIRD LINE: SIGNATURE VERIFICATION
        # can we decrypt signature?
        val_array = val.split(sep2)
        # self.log('val_array =',val_array)
        time_b,sender_pubkey_b,receiver_pubkey_b,msg,signature = val_array
        if not signature: 
            raise Exception('no signature!')
            return None
        sender_pubkey=load_pubkey(sender_pubkey_b)
        authentic = verify_signature(signature,msg,sender_pubkey)
        if not authentic: 
            raise Exception('inauthentic message')
            return None


        # ### FOURTH LINE: CONTENT ENCRYPTION
        # if private_key is None:
        #     private_key=self.private_key_global

        WDV={
            'time':float(time_b.decode('utf-8')),
            'val':msg.decode('utf-8'),
            'channel':key_used
            # 'to':receiver_pubkey_b,
            # 'from':sender_pubkey_b,
            # 'sign':signature
        }

        self.log('GOT WDV:',WDV)
        return WDV
        
        
         #,signature

    # async def set_on_channel(self,key_or_keys,value_or_values):
    #     tasks=[]
    #     if type(channel_or_channels) not in {list,tuple}:
    #         channels=[channel_or_channels]
    #     else:
    #         channels=channel_or_channels

    #     for channel in channels:
    #         uri = 
    #         tasks.append(self.set)

    #     if type(channel_or_channels) == str:
    #         return await self.set(self,key_or_keys,value_or_values,channel_or_channels)
    #     elif type(channel_or_channels) == 
    
    async def set(self,key_or_keys,value_or_values,private_signature_key=None,encode_data=True,encrypt_for_pubkey=None):
        self.log(f'api.set({key_or_keys}) --> {type(value_or_values)}')
        async def _set():
            # self.log('async _set()',self.node)
            # node=self.node
            #node=await _getdb(self)
            node=await self.node

            def proc(key,value):
                self.log(f'encodeing data for {key} -> {type(value)} ...')
                if encode_data and encrypt_for_pubkey is not None and type(value)==bytes:
                    x = self.encode_data(
                        val = value,
                        do_encrypt=False,
                        encrypt_for_pubkey=encrypt_for_pubkey,
                        private_signature_key=private_signature_key
                    )
                    self.log(f'got back encoded data for {key} -> {x} ...')
                    return x
                else:
                    self.log(f'did not encode data for {key} -> {value} ...')
                    return value
                
            if type(key_or_keys) in {list,tuple,dict}:
                keys = key_or_keys
                values = value_or_values
                assert len(keys)==len(values)
                res=[]
                for key,value in zip(keys,values):
                    newval = proc(key,value)
                    self.log(f'kvv (plural) <- {keys}:{value} -> {newval}')
                    await node.set(key,newval)
                    res+=[newval]
            else:
                key = key_or_keys
                value = value_or_values
                newval = proc(key,value)
                self.log(f'kvv (singular) <- {key}:{value} -> {newval}')
                res = newval
                await node.set(key,newval)

            self.log(f'api.set(key={key_or_keys}, \
                        res = {res})')
            #node.stop()
            # self.log('reconnecting ...',self._node)
            #await self._node.stop()
            #await self.connect()
            return res

        return await _set()

    async def get_json(self,key_or_keys,decode_data=False):
        
        def jsonize_dat(dat_dict):
            if type(dat_dict)==dict and 'val' in dat_dict:
                self.log('is this json???',dat_dict['val'],'???')
                dat_dict['val']=json.loads(dat_dict['val'])
                #dat_dict['val']=json.loads(base64.b64decode(dat_dict['val']).decode('utf-8'))
            return dat_dict

        def jsonize_res(res):
            if not res:
                return None
            if type(res)==list:
                return [jsonize_dat(d) for d in res]
            else:
                return jsonize_dat(res)

        res = await self.get(key_or_keys,decode_data=decode_data)
        self.log('get_json() got from get() a',type(res))
        return jsonize_res(res)
           


        

        


    async def set_json(self,key,value,private_signature_key=None,encode_data=True,encrypt_for_pubkey=None):
        #def jsonize_dat(dat_dict):
            #if type(dat_dict)==dict and 'val' in dat_dict:
            #    self.log('is this json???',dat_dict['val'],'???')
            #    dat_dict['val']=json.loads(dat_dict['val'].decode('utf-8'))
            #    #dat_dict['val']=json.loads(base64.b64decode(dat_dict['val']).decode('utf-8'))
        #    return dat_dict

        def prep_json(val):
            if type(val)!=str:
                val=json.dumps(value)
            bval=val.encode('utf-8')
            return bval
            
        
        self.log(f'api.set_json({key}, {value} ...)')
        json_b = prep_json(value)
        self.log(f'bjson -> {json_b}')
        set_res = await self.set(
            key,
            json_b,
            private_signature_key=private_signature_key,
            encode_data=encode_data,
            encrypt_for_pubkey=encrypt_for_pubkey)
        self.log(f'api.set_json() <-- {set_res}')
        return set_res

    async def has(self,key):
        val=await self.get(key)
        return val is not None


    ## PERSONS
    async def get_person(self,username):
        return await self.get('/pubkey/'+username,decode_data=False)

    async def set_person(self,username,pem_public_key):
        # pem_public_key = save_public_key(public_key,return_instead=True)
        #obj = {'name':username, 'public_key':pem_public_key}
        # await self.set_json('/person/'+username,obj)
        # keystr=base64.b64encode(pem_public_key).decode()
        # self.log('keystr',type(keystr))
        await self.set('/pubkey/'+username,pem_public_key,encode_data=False)
        # keystr=pem_public_key
        # await self.set(b'/name/'+keystr,username,encode_data=False)






    ## Register
    async def register(self,name,passkey=None,just_return_keys=False):
        # if not (name and passkey): return {'error':'Name and password needed'}
        import kademlia
        try:
            person = await self.get_person(name)
        except kademlia.network.CannotReachNetworkError:
            return {'error':'Network disconnected'}
        except NetworkStillConnectingError:
            return {'error':'Network still connecting...'}

        keys = self.get_keys()
        if person is not None:
            self.log('register() person <-',person)
            # try to log in
            
            self.log('my keys',keys)
            if not name in keys: 
                self.log('!! person already exists')
                return {'error':'Person already exists'}
            
            # test 3 conditions
            privkey=keys[name]
            pubkey=load_pubkey(person)

            if simple_lock_test(privkey,pubkey):
                self.username=name
                self.log('!! logging into',name)
                return {'success':'Logging back in...'}

        private_key = generate_rsa_key()
        public_key = private_key.public_key()
        pem_private_key = serialize_privkey(private_key, password=passkey)# save_private_key(private_key,password=passkey,return_instead=True)
        pem_public_key = serialize_pubkey(public_key)

        if just_return_keys:
            return (pem_private_key,pem_public_key)

        # save pub key in db
        await self.set_person(name,pem_public_key)
        # save priv key on hardware
        fn_privkey = os.path.join(KEYDIR,f'.{name}.key')

        self.log('priv key =',pem_private_key)
        write_key_b(pem_private_key, fn_privkey)

        # good
        return {'success':'Person created ...', 'username':name}
    

    def load_private_key(self,password):
        #if not self.app_storage.exists('_keys'): return {'error':'No login keys present on this device'}
        pem_private_key=self.app_storage.get('_keys').get('private')
        # self.log('my private key ====',pem_private_key)
        try:
            return {'success':load_privkey(pem_private_key,password)}
        except ValueError as e:
            self.log('!!',e)
        return {'error':'Incorrect password'}

    def add_world_key(self,fn=PATH_WORLD_KEY):
        import shutil
        thisdir=os.path.dirname(__file__)
        fnfn=os.path.join(thisdir,fn)
        self.log('getting',fnfn)
        name='.'.join(os.path.basename(fn).split('.')[1:-1])

        priv_key=load_privkey_fn(fnfn)
        pub_key=priv_key.public_key()
        pub_key_b=serialize_pubkey(pub_key)

        ofn=os.path.join(KEYDIR,f'.{name}.key')
        shutil.copyfile(fnfn,ofn)

        asyncio.create_task(self.add_world_key_to_net(name,pub_key_b))
        
    async def add_world_key_to_net(self,name,pub_key_b):
        await self.set_person(name,pub_key_b)
            
    #@property
    def get_keys(self):
        res={}
        key_files = os.listdir(KEYDIR)
        world_key_fn = os.path.basename(PATH_WORLD_KEY)
        if not world_key_fn in key_files:
            self.log('[first time?] adding world key:',world_key_fn)
            self.add_world_key()
            

        for priv_key_fn in key_files:
            if (not priv_key_fn.startswith('.') or not priv_key_fn.endswith('.key')): continue
            fnfn = os.path.join(KEYDIR,priv_key_fn)
            print(fnfn)
            priv_key=load_privkey_fn(fnfn)
            #pub_key=priv_key.public_key()
            name_key= '.'.join(priv_key_fn.split('.')[1:-1])
            res[name_key] = priv_key
            self.log(f'[API] found key {name_key} and added to keychain')
        return res
            

    @property
    def keys(self):
        if not hasattr(self,'_keys'):
            self.load_keys()
        return self._keys

    def load_keys(self):
        self._keys = self.get_keys()        
        


    async def append_data(self,uri,bdata):
        self.log(f'appending to uri {uri}, data {bdata}')
        if type(bdata)!=bytes and type(bdata)==str:
            bdata=bdata.encode('utf-8')
            self.log(f'--> encoded bdata to {bdata}')

        # get blob so far
        sofar = await self.get(uri,decode_data=False)

        # get sofar
        self.log(f'sofar = {sofar}')
        
        newval = bdata if sofar is None else sofar+BSEP+bdata
        self.log(f'newval = {newval}')

        res = await self.set(uri,newval,encode_data=False)
        if res:
            length = newval.count(BSEP)+1
            return {'success':'Length increased to %s' % length}
        return {'error':'Could not append data'}

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
        


    async def post(self,data,channel,add_to_outbox=True):
        post_id=get_random_id()
        #tasks = []

        self.log(f'api.post({data},add_to_outbox={add_to_outbox}) --> ...')
        # stop
        
        # ## add to inbox
        post_id = get_random_id()
        self.load_keys()
        author_privkey = self.keys[data.get('author')]
            
        self.log('ADDING TO CHANNEL??',channel)
        pubkey_channel = self.keys[channel].public_key()

        ## 1) STORE ACTUAL CONTENT OF POST UNDER CENTRAL POST URI
        # HAS NO CHANNEL: just one post/msg in a sea of many
        # e.g. /post/5e4a355873194399a5b356def5f40ff9
        # does not reveal who cand decrypt it
        uri = '/post/'+post_id
        json_res = await self.set_json(
            uri,
            data, #data_channel, 
            encode_data=True, 
            encrypt_for_pubkey=pubkey_channel,
            private_signature_key=author_privkey
            )
        self.log(f'json_res() <- {json_res}')
        
        
        ## 2) Store under the channels a reference to the post,
        # as a hint they may be able to decrypt it with one of their keys
        add_post_id_as_hint_to_channels = [f'/inbox/{channel}']
        if add_to_outbox:
            un=data.get('author')
            if un:
                add_post_id_as_hint_to_channels += [f'/outbox/{un}']
        tasks = [
            self.append_data(uri,post_id) for uri in add_post_id_as_hint_to_channels
        ]
        res = await asyncio.gather(*tasks)
        if res and all([(d and 'success' in d) for d in res]):
            return {'success':'Posted! %s' % post_id, 'post_id':post_id}
        
        return {'error':'Post unsuccessful'}

        # append_res=await self.append_json(f'/inbox/{channel}',post_id)
        # self.log(f'json_res.append_json({channel}) <- {append_res}')
        # #tasks.append(task)

        # # add to outbox
        # if add_to_outbox:
        #     un=data.get('author')
        #     if un:
        #         append_res = await self.append_json(f'/outbox/{un}', post_id)
        #         self.log(f'json_res.append_json({un}) <- {append_res}')
        #         #tasks.append(task)

        #asyncio.create_task(self.flush())
        # return {'success':'Posted! %s' % post_id, 'post_id':post_id}
        #return {'error':'Post failed'}

    async def get_json_val(self,uri,decode_data=True):
        res=await self.get_json(uri,decode_data=decode_data)
        self.log('get_json_val() got from get_json():',res,type(res))
        
        r=res
        if type(res) == dict:
            r=res.get('val',None) if res is not None else res
        elif type(res) == list:
            r=[(x.get('val') if type(x)==dict else x) for x in res if x is not None]
        elif type(res) == str:
            r=json.loads(res)
        self.log(f'get_json_val() --> {r} {type(r)}')
        return r

    async def get_post(self,post_id):
        self.log(f'api.get_post({post_id}) ?')
        post_json = await self.get_json('/post/'+post_id, decode_data=True)
        self.log(f'api.get_post({post_id}) --> {post_json}')
        return post_json

    async def get_post_ids(self,uri='/inbox/world'):
        ## GET POST IDS
        self.log(f'api.get_post_ids(uri={uri}) ?')
        index = await self.get(uri,decode_data=False)
        self.log(f'api.get_post_ids(uri={uri}) <-- api.get()',index)
        if not index: return []

        #index = json.loads(base64.b64decode(index).decode())
        index = [x.decode('utf-8') for x in index.split(BSEP)]
        
        if index is None: return []
        if type(index)!=list: index=[index]
        index = [x for x in index if x is not None]
        
        self.log(f'api.get_post_ids({uri}) --> {index}')
        return index

    async def get_posts(self,uri='/inbox/world'):

        # get IDs
        post_ids = await self.get_post_ids(uri)
        
        # get posts
        posts = [self.get_post(post_id) for post_id in post_ids]
        return await asyncio.gather(*posts)
        




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
    
    # api.set(['a','b','c'],[1,2,3])
    async def run():
        api = Api()
        # await api.connect()
        
        #await api.set_json('whattttt',{'aaaaa':12222})
        #await api.set_json('whattttt',[111])
        #await api.set_json('whattttt',[111])
        
        #val = await api.get_json('whattttt')
        
        server = await _getdb(api)
        await server.set('a',1)
        print(await server.get('a'))
        await asyncio.sleep(5)
        await server.set('a',2)

        print(await server.get('a'))
        await asyncio.sleep(5)

        await server.set('a',str([2,3,4,5]))
        print(await server.get('a'))
        await asyncio.sleep(5)

        val = await server.get('a')
        
        

        print(f'VAL = {val}')
        return val
    
    asyncio.run(run())


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
        await node.set("my-key", "my awesome value2")
        await node.set("my-key", "my awesome value3")


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



async def lonely_selfless_node():
    from api import Api,PORT_LISTEN
    API = Api()
    return await API.connect_forever(8467)


def boot_lonely_selfless_node(port=8467):
    API = Api()
    asyncio.run(API.connect_forever())
    

def init_entities(usernames = ['world']):
    ## make global entity called world
    
    #loop=asyncio.new_event_loop()

    async def register(username):
        API = Api() 
        #await API.connect_forever()
        #privkey,pubkey = await API.register(username,just_return_keys=True)

        private_key = generate_rsa_key()
        public_key = private_key.public_key()
        pem_private_key = serialize_privkey(private_key)
        pem_public_key = serialize_pubkey(public_key)


        privkey_fn = os.path.join(KEYDIR_BUILTIN,f'.{username}.key.priv')
        pubkey_fn = os.path.join(KEYDIR_BUILTIN,f'.{username}.key.pub')
        with open(privkey_fn,'wb') as of: of.write(pem_private_key)
        with open(pubkey_fn,'wb') as of: of.write(pem_public_key)
        # print(API.keys)

        await API.set_person(username,pem_public_key)
        print('done')


    for un in usernames:
        asyncio.run(register(un))
    

def split_binary(data, sep=BSEP):
    seplen = len(BSEP)
    res=[]
    stack=None
    print('!!',data[:4],seplen,sep)

    cutoffs=[]
    for i in range(0, len(data)):
        seg=data[i:i+seplen]
        print(i,seg,sep,stack)
        if seg==sep:
            # split_piece = data[:i+seplen]
            print('!')
            cutoff_lasttime = cutoffs[-1][-1] if cutoffs and cutoffs else 0
            cutoff = (cutoff_lasttime-seplen, i)
            print(cutoff)
            cutoffs.append(cutoff)
            stack = data[cutoff[0] if cutoff[0]>0 else 0: cutoff[1]]
            print(stack)
            res += [stack]
            stack = None

    cutoff_lasttime = cutoffs[-1][-1] if cutoffs and cutoffs else 0
    print(cutoff_lasttime)
    stack = data[cutoff_lasttime+seplen :]
    res+=[stack]
    print('RES:',res)
    return res





if __name__=='__main__':
    init_entities()

    # res = split_binary(b'eeeehey||||whatsueep',b'||||')
    # print(res)