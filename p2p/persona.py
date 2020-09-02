import os
import asyncio
from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.exception import ThemisError
from base64 import b64decode,b64encode
# from kademlia.network import Server
import os,time,sys,logging
from pathlib import Path

sys.path.append('../p2p')
BSEP=b'||||||||||'
BSEP2=b'@@@@@@@@@@'
BSEP3=b'##########'
NODE_SLEEP_FOR=1

P2P_PREFIX=b'/persona/'
P2P_PREFIX_POST=b'/msg/'
P2P_PREFIX_INBOX=b'/inbox/'
P2P_PREFIX_OUTBOX=b'/outbox/'

WORLD_PUB_KEY = b'VUVDMgAAAC1z53KeApQY4RICK5k0nXnnS+K17veIFMPlFKo7mqnRhTZDhAmG'
WORLD_PRIV_KEY = b'UkVDMgAAAC26HXeGACxZUoKYKlZ7sDmVoLwffNj3CrdqoPrE94+2ysfhufmP'

KOMRADE_PUB_KEY = b'VUVDMgAAAC09uo+wAgu/V9xyvMkMDbOQEk1ssOrFADaiyTzfwVjE6o8FHoil'
KOMRADE_PRIV_KEY = b'UkVDMgAAAC33fFiaAIpmQewjkYndzMcMkj1mLy/lE4RXJQzIlUN94tyC5g29'

DEBUG = True
UPLOAD_DIR = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

PORT_LISTEN = 5639
NODE_SLEEP_FOR=1
NODES_PRIME = [("128.232.229.63",8467)] 



KEY_PATH = os.path.join(os.path.expanduser('~'),'.komrade')
KEY_PATH_PUB = os.path.join(KEY_PATH,'.locs')
KEY_PATH_PRIV = os.path.join(KEY_PATH,'.keys')

for x in [KEY_PATH,KEY_PATH_PUB,KEY_PATH_PRIV]:
    if not os.path.exists(x): os.makedirs(x)

WORLD_PRIV_KEY_FN = os.path.join(KEY_PATH_PRIV,'.world.key')
WORLD_PUB_KEY_FN = os.path.join(KEY_PATH_PUB,'.world.loc')
KOMRADE_PRIV_KEY_FN = os.path.join(KEY_PATH_PRIV,'.komrade.key')
KOMRADE_PUB_KEY_FN = os.path.join(KEY_PATH_PUB,'.komrade.loc')


def check_world_keys():
    if not os.path.exists(WORLD_PRIV_KEY_FN):
        with open(WORLD_PRIV_KEY_FN,'wb') as of:
            of.write(WORLD_PRIV_KEY)
    
    if not os.path.exists(WORLD_PUB_KEY_FN):
        with open(WORLD_PUB_KEY_FN,'wb') as of:
            of.write(WORLD_PUB_KEY)

    if not os.path.exists(KOMRADE_PRIV_KEY_FN):
        with open(KOMRADE_PRIV_KEY_FN,'wb') as of:
            of.write(KOMRADE_PRIV_KEY)
    
    if not os.path.exists(KOMRADE_PUB_KEY_FN):
        with open(KOMRADE_PUB_KEY_FN,'wb') as of:
            of.write(KOMRADE_PUB_KEY)
    
check_world_keys()


## CONNECTING




## utils

def get_random_id():
    import uuid
    return uuid.uuid4().hex

def get_random_binary_id():
    import base64
    idstr = get_random_id()
    return base64.b64encode(idstr.encode())


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



class NetworkStillConnectingError(OSError): pass







class Persona(object):

    def __init__(self,name,api=None,node=None,create_if_missing=True):
        self.name=name
        self.log=log
        self.privkey=None
        self.pubkey=None
        self.api=api
        # self._node=node
        self.create_if_missing=create_if_missing
        self.log(f'>> Persona.__init__(name={name},create_if_missing={create_if_missing})')

        # load at least any local keys (non-async)
        self.find_keys_local()

    

    def __repr__(self):
        #pkeystr = '+loc' if self.has_public_key() else ''
        #privkeystr = ' +key' if self.has_private_key() else ''
        # ptypestr='acccount' if self.has_private_key() else 'contact'
        ptypestr='loc' if not self.has_private_key() else 'keyloc'

        return f'{self.name} ({ptypestr})'

    
    def has_private_key(self):
        return self.privkey is not None
    
    def has_public_key(self):
        return self.pubkey is not None
    

    @property
    async def node(self):
        node = await self.api.node
        return node


    async def boot(self):
        self.log(f'>> Persona.boot()')
        # self.load_or_gen()
        await self.find_keys()
        if self.pubkey is None and self.create_if_missing:
            self.gen_keys()
            await self.set_pubkey_p2p()

        if self.privkey and self.pubkey:
            return {'success':'Logged in...'}
        return {'error':'Login failed'}


    @property
    def key_path_pub(self):
        return os.path.join(KEY_PATH_PUB,'.'+self.name+'.loc')

    @property
    def key_path_priv(self):
        return os.path.join(KEY_PATH_PRIV,'.'+self.name+'.key')
    
    @property
    def name_b64(self):
        return b64encode(self.name.encode())

        
    @property
    def privkey_b64(self):
        return b64encode(self.privkey)

    @property
    def pubkey_b64(self):
        return b64encode(self.pubkey)
    ## genearating keys
    
    def gen_keys(self):
        self.log('gen_keys()')
        keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
        self.privkey = keypair.export_private_key()
        self.pubkey = keypair.export_public_key()

        self.log(f'priv_key saved to {self.key_path_priv}')
        with open(self.key_path_priv, "wb") as private_key_file:
            private_key_file.write(self.privkey_b64)

        with open(self.key_path_pub, "wb") as public_key_file:
           public_key_file.write(self.pubkey_b64)
        

    ## loading keys from disk

    def find_keys_local(self):
        self.log(f'find_keys_local(path_pub={self.key_path_pub}, path_priv={self.key_path_priv})')

        if os.path.exists(self.key_path_pub):
            with open(self.key_path_pub) as pub_f:
                self.pubkey=b64decode(pub_f.read())

        if os.path.exists(self.key_path_priv):
            with open(self.key_path_priv) as priv_f:
                self.privkey=b64decode(priv_f.read())
 
    ## finding on p2p net
    async def find_keys_p2p(self,name=None):
        await self.node
        
        if not name: name=self.name
        self.log(f'find_keys_p2p(name={name})')
        name_b64=b64encode(name.encode())
        

        node = await self.node
        key=P2P_PREFIX+name.encode()

        self.log(f'LOOKING FOR: {key}')
        res = await node.get(key)
        self.log(f'FOUND: {res}')

        if res is not None:
            signed_msg,pubkey_b64 = b64decode(res).split(BSEP)
            self.log('!!!!!',signed_msg,pubkey_b64)
            verified_msg = self.verify(signed_msg,pubkey_b64)

            if verified_msg is not None:
                self.log('verified message!',verified_msg)
                name,pubkey_b64 = verified_msg.split(BSEP2)
                self.pubkey = b64decode(pubkey_b64)
                self.name = b64decode(name).decode()
                print('>> found pubkey!',self.pubkey_b64,'and name',self.name)

                ## save back to cache?
                self.save_pubkey(pubkey_b64)

    async def find_keys(self):
        #self.find_keys_local()   # <- now doing this, which is not async, in __init__()
        if self.pubkey is None:
            await self.find_keys_p2p()
            # if self.pubkey is not None:
            #     # save back to local cache?

    def save_pubkey(self,pubkey_b64):
        with open(self.key_path_pub, "wb") as public_key_file:
           public_key_file.write(pubkey_b64)
           self.log('>> saved:',self.key_path_pub)

    async def set_pubkey_p2p(self):
        # signed_name = self.sign(b64encode(self.name.encode()))
        # signed_pubkey_b64 = self.sign(self.pubkey_b64)
        
        self.log(f'set_pubkey_p2p()...')
        
        signed_msg = self.sign(self.name_b64 + BSEP2 + self.pubkey_b64)
        package = b64encode(signed_msg + BSEP +self.pubkey_b64)
        #await self.api.set('/pubkey/'+self.name,package,encode_data=False)

        key=P2P_PREFIX+self.name.encode()
        newval=package
        self.log('set_pubkey()',key,'-->',newval)
        node = await self.node
        return await node.set(key,newval)




    ## E/D/S/V

    def encrypt(self,msg_b64,for_pubkey_b64):
        # handle verification failure
        for_pubkey = b64decode(for_pubkey_b64)
        encrypted_msg = SMessage(self.privkey, for_pubkey).wrap(msg_b64)
        return b64encode(encrypted_msg)

    def decrypt(self,encrypted_msg_b64,from_pubkey_b64):
        # handle verification failure
        from_pubkey = b64decode(from_pubkey_b64)
        encrypted_msg = b64decode(encrypted_msg_b64)
        decrypted_msg = SMessage(self.privkey, from_pubkey).unwrap(encrypted_msg)
        return decrypted_msg

    def sign(self,msg):
        signed_msg = b64encode(ssign(self.privkey, msg))
        return signed_msg

    def verify(self,signed_msg_b64,pubkey_b64):
        signed_msg = b64decode(signed_msg_b64)
        public_key = b64decode(pubkey_b64)
        try:
            verified_msg = sverify(public_key, signed_msg)
            return verified_msg
        except ThemisError as e:
            print('!!',e)
            return None
    

    ## EVEN HIGHER LEVEL STUFF: person 2 person

    @property
    async def world(self): return self.api.keys['world']

    @property
    async def komrade(self): return self.api.keys['komrade']


    async def send(self,msg_b,to):
        return await self.api.send(msg_b,self,to)


    @property
    def uri_inbox(self):
        return P2P_PREFIX_INBOX+self.name.encode()

    @property
    def uri_outbox(self):
        return P2P_PREFIX_OUTBOX+self.name.encode()

    @property
    def app_person(self):
        return self.api.keys['komrade']

    @property
    def app_pubkey_b64(self):
        return self.app_person.pubkey_b64

    async def load_inbox(self,decrypt_msg_uri=False,last=None):
        node = await self.node
        encrypted_inbox_idstr_b64 = await node.get(self.uri_inbox)
        self.log('encrypted_inbox_idstr_b64 =',encrypted_inbox_idstr_b64)
        if encrypted_inbox_idstr_b64 is None: return []
        
        # inbox_idstr = self.decrypt(encrypted_inbox_idstr_b64, self.app_pubkey_b64)
        # self.log('decrypted inbox_idstr =',inbox_idstr)
        # decrypt!

        encrypted_inbox_idstr = b64decode(encrypted_inbox_idstr_b64)
        self.log('encrypted_inbox_idstr =',encrypted_inbox_idstr)

        inbox_ids = encrypted_inbox_idstr.split(BSEP) if encrypted_inbox_idstr is not None else []
        self.log('inbox_ids =',inbox_ids)
        
        if decrypt_msg_uri:
            inbox_ids = [self.decrypt(enc_msg_id_b64,self.app_person.pubkey_b64) for enc_msg_id_b64 in inbox_ids]
            self.log('inbox_ids decrypted =',inbox_ids)

        return inbox_ids[:last]

    async def add_to_inbox(self,msg_uri,inbox_sofar=None):
        # encrypt msg id so only inbox owner can resolve the pointer
        self.log('unencrypted msg uri:',msg_uri)
        encrypted_msg_uri = self.app_person.encrypt(msg_uri, self.pubkey_b64)
        self.log('encrypted msg uri:',encrypted_msg_uri)

        # get current inbox
        if inbox_sofar is None: inbox_sofar=await self.load_inbox()
        self.log('inbox_sofar:',inbox_sofar)

        # add new value
        new_inbox = inbox_sofar + [encrypted_msg_uri]
        new_inbox_b = BSEP.join(new_inbox)
        self.log('new_inbox_b:',new_inbox_b)

        new_inbox_b64 = b64encode(new_inbox_b)

        self.log('new_inbox_b64:',new_inbox_b64)

        # set on net
        node = await self.node
        await node.set(self.uri_inbox,new_inbox_b64)

        new_length = len(new_inbox)
        return {'success':'Inbox length increased to %s' % new_length}
        #return {'error':'Could not append data'}


    async def add_to_outbox(self):
        """
        Do not store on server!
        """
        pass

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
            


def run_multiple_tasks(tasks):
    async def _go(tasks):
        res = await asyncio.gather(*tasks, return_exceptions=True)
        return res
    return asyncio.get_event_loop().run_until_complete(_go(tasks))

async def main():

    # start node
    from kademlia.network import Server
    #from p2p_api import 
    PORT_LISTEN = 5969

    # NODES_PRIME = [("128.232.229.63",8467), ("68.66.241.111",8467)] 
    NODES_PRIME = [("128.232.229.63",8467)] 

    node = Server(log=log)
    await node.listen(PORT_LISTEN)
    await node.bootstrap(NODES_PRIME)
    
    marx = Persona('marx',node=node)
    elon = Persona('elon2',node=node)
    world = Persona('world',node=node)
    await world.boot()

    # komrade = Persona('komrade')
    # await komrade.boot()
    

    await marx.boot()
    await elon.boot()

    # await marx.send(b'Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! Secret message 2! ',to=elon)


    # await elon.read_inbox()

    await marx.send(b'A specter is haunting the internet',to=world)
    await elon.send(b'My rockets explode and so will your mind',to=world)
    await elon.send(b'My rockets explode and so will your mind',to=world)

    await world.read_inbox()

    return True
    

if __name__=='__main__':
    asyncio.run(main())














