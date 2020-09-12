import os
import asyncio
from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.exception import ThemisError
from pythemis.scell import SCellSeal

from base64 import b64decode,b64encode
# from kademlia.network import Server
import os,time,sys,logging
from pathlib import Path
import requests

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
KEYSERVER_ADDR = 'komrade.app' #'128.232.229.63'
KEYSERVER_PORT = 5566


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
    
# check_world_keys()


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

        self.can_receive = False
        self.can_send = False
        # self.can_login = False
        self.external_keys_loaded = False


        self.pubkey_enc = None
        self.pubkey_decr = None

        # self._node=node
        self.create_if_missing=create_if_missing
        # self.log(f'>> Persona.__init__(name={name},create_if_missing={create_if_missing})')

        # load at least any local keys (non-async)
        self.find_keys_local()
        # self.login_or_register()

    

    def __repr__(self):
        #pkeystr = '+loc' if self.has_public_key() else ''
        #privkeystr = ' +key' if self.has_private_key() else ''
        # ptypestr='acccount' if self.has_private_key() else 'contact'
        ptypestr='loc' if not self.has_private_key() else 'keyloc'

        return f'{self.name} ({ptypestr})'

    def get_keyserver_pubkey(self):
        Q=f'http://{KEYSERVER_ADDR}:{KEYSERVER_PORT}/pub'
        
        r = self.api.request(Q)
        return r.content
        # self.log('r =',r,b64encode(r.content))
        # pubkey_b64 = b64encode(r.content)
        # return pubkey_b64

    def get_externally_signed_pubkey(self):
        Q=f'http://{KEYSERVER_ADDR}:{KEYSERVER_PORT}/get/{self.name}'
        self.log('Q:',Q)
        r = self.api.request(Q)
        package_b64 = r.content
        package = b64decode(package_b64)
        self.log('package <--',package)
        if not package: return (b'',b'',b'')
        return package.split(BSEP)
        # pubkey_b64, signed_pubkey_b64, server_signed_pubkey_b64 = package.split(BSEP)
        
        # signed_pubkey = b64encode(r.content)
        # return (b64encode(pubkey), b64encode(signed_pubkey))

    def set_externally_signed_pubkey(self):
        import requests
        Q=f'http://{KEYSERVER_ADDR}:{KEYSERVER_PORT}/add/{self.name}' #/{name}/{key}
        
        package = self.pubkey_b64 + BSEP + self.signed_pubkey_b64
        self.log('set_externally_signed_pubkey package -->',package)

        r = requests.post(Q, data=package) #{'name':self.name,'key':self.pubkey_b64})
        return r
    
    def has_private_key(self):
        return self.privkey is not None
    
    def has_public_key(self):
        return self.pubkey is not None
    

    @property
    async def node(self):
        node = await self.api.node
        return node


    def load_keyserver_pubkey(self):
        self.keyserver_pubkey_b64 = self.get_keyserver_pubkey()
        self.keyserver_pubkey = b64decode(self.keyserver_pubkey_b64)
        self.log('keyserver_pubkey =',self.keyserver_pubkey)
        return self.keyserver_pubkey

    def load_external_keys(self):
        if self.external_keys_loaded: return

        self.pubkey_ext_b64, self.signed_pubkey_ext_b64, self.server_signed_pubkey_ext_b64 = self.get_externally_signed_pubkey()
        self.log('pubkey_ext_b64 =',self.pubkey_ext_b64)
        self.log('signed_pubkey_ext_b64 =',self.signed_pubkey_ext_b64)
        self.log('server_signed_pubkey_ext_b64 =',self.server_signed_pubkey_ext_b64)
        self.external_keys_loaded = True

    def keyserver_name_exists(self):
        user_missing = (self.pubkey_ext_b64 is b'' or self.signed_pubkey_ext_b64 is b'' or self.server_signed_pubkey_ext_b64 is b'')
        return not user_missing


    def meet(self,save_loc=True):
        pubkey_ext = b64decode(self.pubkey_keyserver_verified)
        self.log('pubkey_ext',pubkey_ext)
        self.pubkey=pubkey_ext
        self.log('setting self.pubkey to external value:',self.pubkey)
        self.log('self.pubkey_64',self.pubkey_b64)
        self.log('keyserver_verified',self.pubkey_keyserver_verified)
        
        with open(self.key_path_pub,'wb') as of:
            of.write(self.pubkey_keyserver_verified)
        
        return {'success':'Met person as acquaintance'}

    def register(self):
        # register
        if self.create_if_missing:
            self.gen_keys()
            res = self.set_externally_signed_pubkey()
            self.log('set_externally_signed_pubkey res =',res)
            if res is None:
                return {'error':'Could not set externally signed pubkey'}
            else:
                return {'success':'Created new pubkey'}
        else:
            return {'error':'No public key externally, but create_if_missing==False'}


    # login, meet, or register
    def boot(self):
        # keyserver active?
        keyserver_pubkey = self.keyserver_pubkey = self.load_keyserver_pubkey()
        if keyserver_pubkey is None:
            return {'error':'Cannot conntact keyserver'}
        
        # load external keys
        self.load_external_keys()

        # user exists...
        if self.keyserver_name_exists():

            # if I claim to be this person
            if self.privkey and self.pubkey_decr:
                attempt = self.login()
                self.log('login attempt ->',attempt)
                return attempt

            # otherwise just meet them
            attempt = self.meet()
            self.log('meet attempt ->',attempt)
            return attempt

        # user does not exist
        attempt = self.register()
        self.log('register attempt -->',attempt)
        return attempt
    
    @property
    def key_path_pub(self):
        return os.path.join(KEY_PATH_PUB,'.'+self.name+'.loc')

    @property
    def key_path_pub_enc(self):
        return os.path.join(KEY_PATH_PUB,'.'+self.name+'.loc.box')


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
        return b64encode(self.pubkey) if self.pubkey else b''
    
    @property
    def signed_pubkey_b64(self):
        return self.sign(self.pubkey_b64)
        # return self.encrypt(self.pubkey_b64, self.pubkey_b64)
    
    ## genearating keys
    
    # def gen_keys1(self):
    #     self.log('gen_keys()')
    #     keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
    #     self.privkey = keypair.export_private_key()
    #     self.pubkey = keypair.export_public_key()

    #     self.log(f'priv_key saved to {self.key_path_priv}')
    #     with open(self.key_path_priv, "wb") as private_key_file:
    #         private_key_file.write(self.privkey_b64)

    #     with open(self.key_path_pub, "wb") as public_key_file:
    #         # save SIGNED public key
    #         public_key_file.write(self.pubkey_b64)
        
    #     with open(self.key_path_pub_enc,'wb') as signed_public_key_file:
    #         # self.log('encrypted_pubkey_b64 -->',self.encrypted_pubkey_b64)
    #         pubkey_b64 = b64encode(self.pubkey)
    #         self.log('pubkey',self.pubkey)
    #         self.log('pubkey_b64',pubkey_b64)
            
    #         encrypted_pubkey_b64 = self.encrypt(pubkey_b64, pubkey_b64, KOMRADE_PRIV_KEY)
    #         self.log('encrypted_pubkey_b64 -->',encrypted_pubkey_b64)
            
    #         signed_public_key_file.write(encrypted_pubkey_b64)

    def gen_keys(self,passphrase=DEBUG_DEFAULT_PASSPHRASE):
        """
        Generate private/public key pair
        Secure that with passphrase
        """

        ## Generate key pair
        self.log('gen_keys()')
        keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
        self.privkey = keypair.export_private_key()
        self.pubkey = keypair.export_public_key()

        ## Secure with passphrase
        if passphrase is None: passphrase=input('Please protect account with passphrase:\n')
        cell = SCellSeal(passphrase=passphrase)
        keypair_b = self.privkey + BSEP + self.pubkey
        
        keypair_b_encr = cell.encrypt(keypair_b)


        self.log(f'priv_key saved to {self.key_path_priv}')
        with open(self.key_path_priv, "wb") as private_key_file:
            private_key_file.write(self.privkey_b64)

        with open(self.key_path_pub, "wb") as public_key_file:
            # save SIGNED public key
            public_key_file.write(self.pubkey_b64)
        
        with open(self.key_path_pub_enc,'wb') as signed_public_key_file:
            # self.log('encrypted_pubkey_b64 -->',self.encrypted_pubkey_b64)
            pubkey_b64 = b64encode(self.pubkey)
            self.log('pubkey',self.pubkey)
            self.log('pubkey_b64',pubkey_b64)
            
            encrypted_pubkey_b64 = self.encrypt(pubkey_b64, pubkey_b64, KOMRADE_PRIV_KEY)
            self.log('encrypted_pubkey_b64 -->',encrypted_pubkey_b64)
            
            signed_public_key_file.write(encrypted_pubkey_b64)
        

    ## loading keys from disk

    def find_keys_local(self):
        self.log(f'find_keys_local(path_pub={self.key_path_pub}, path_priv={self.key_path_priv})')

        if os.path.exists(self.key_path_priv):
            with open(self.key_path_priv) as priv_f:
                self.privkey=b64decode(priv_f.read())

        # Load from encrypted?
        if os.path.exists(self.key_path_pub_enc) and self.privkey:
            with open(self.key_path_pub_enc) as pub_f:
                self.pubkey_enc=pub_f.read()
                self.pubkey_decr=self.decrypt(self.pubkey_enc, KOMRADE_PUB_KEY)
                # self.pubkey=self.pubkey_decr
                self.log('loaded self.pubkey from enc',self.pubkey)
                self.can_receive = True
                self.can_send = True
        
        # load from nonencrypted pubkey?
        if os.path.exists(self.key_path_pub):
            with open(self.key_path_pub) as pub_f:
                self.pubkey=b64decode(pub_f.read())
                self.log('loaded self.pubkey from UNenc',self.pubkey)
                self.can_receive = True

    @property
    def pubkey_keyserver_verified(self):
        # test if remote data agrees
        if not hasattr(self,'_keyserver_verified'):
            self._keyserver_verified = self.verify(self.server_signed_pubkey_ext_b64, self.keyserver_pubkey_b64)
        return self._keyserver_verified
            
    def login(self):
        # test if local data present
        if not self.pubkey or not self.pubkey_decr:
            return {'error':'Public keys not present'}

        # test if local data agrees
        self.log('self.pubkey',self.pubkey_b64)
        self.log('self.pubkey_decr',self.pubkey_decr)
        if self.pubkey_b64 != self.pubkey_decr:
            return {'error':'Public keys do not match'}

        # test if remote data agrees
        keyserver_verified = self.pubkey_keyserver_verified
        if keyserver_verified is None: 
            return {'error':'Keyserver verification failed'}

        # test if pubkey match
        enc_match = self.pubkey_decr == keyserver_verified
        if enc_match:
            return {'success':'Keys matched'}
        return {'error':'Keys did not match'}

        
    



    ## E/D/S/V

    def encrypt(self,msg_b64,for_pubkey_b64, privkey_b64=None):
        self.log('encrypt()',msg_b64,for_pubkey_b64,privkey_b64)
        
        privkey = b64decode(privkey_b64) if privkey_b64 else self.privkey
        # handle verification failure
        for_pubkey = b64decode(for_pubkey_b64)
        encrypted_msg = SMessage(privkey, for_pubkey).wrap(msg_b64)
        return b64encode(encrypted_msg)

    def decrypt(self,encrypted_msg_b64,from_pubkey_b64, privkey_b64=None):
        privkey = b64decode(privkey_b64) if privkey_b64 else self.privkey

        # handle verification failure
        from_pubkey = b64decode(from_pubkey_b64)
        encrypted_msg = b64decode(encrypted_msg_b64)
        decrypted_msg = SMessage(privkey, from_pubkey).unwrap(encrypted_msg)
        return decrypted_msg

    def sign(self,msg_b64, privkey=None):
        if not privkey: privkey=self.privkey
        signed_msg = b64encode(ssign(privkey, msg_b64))
        return signed_msg

    def verify(self,signed_msg_b64,pubkey_b64=None):
        if pubkey_b64 is None: pubkey_b64=self.pubkey_b64
        
        self.log('verify() signed_msg_b64 =',signed_msg_b64)
        self.log('verify() pubkey_b64 =',pubkey_b64)
        signed_msg = b64decode(signed_msg_b64)
        public_key = b64decode(pubkey_b64)

        self.log('verify() signed_msg =',signed_msg)
        self.log('verify() public_key =',public_key)

        try:
            verified_msg = sverify(public_key, signed_msg)
            return verified_msg
        except ThemisError as e:
            print('!!',e)
            return None
    



    @property
    def uri_inbox(self):
        return P2P_PREFIX_INBOX+self.name.encode()

    @property
    def uri_outbox(self):
        return P2P_PREFIX_OUTBOX+self.name.encode()

    @property
    def app_pubkey_b64(self):
        return KOMRADE_PUB_KEY




    ## POSTING/SENDING MSGS

    async def post(self,encrypted_payload_b64,to_person):
        # double wrap
        double_encrypted_payload = self.encrypt(encrypted_payload_b64, to_person.pubkey_b64, KOMRADE_PRIV_KEY) 
        self.log('double_encrypted_payload =',double_encrypted_payload)

        post_id = get_random_binary_id() #get_random_id().encode()
        node = await self.node

        uri_post = P2P_PREFIX_POST + post_id
        res = await node.set(uri_post, double_encrypted_payload)
        self.log('result of post() =',res)

        return uri_post

    async def send(self,msg_b,to,from_person=None):
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
        to_person = to
        if from_person is None: from_person = self
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
            inbox_ids = [self.decrypt(enc_msg_id_b64,KOMRADE_PUB_KEY) for enc_msg_id_b64 in inbox_ids]
            self.log('inbox_ids decrypted =',inbox_ids)

        return inbox_ids[:last]

    async def add_to_inbox(self,msg_uri,inbox_sofar=None):
        # encrypt msg id so only inbox owner can resolve the pointer
        self.log('unencrypted msg uri:',msg_uri)
        encrypted_msg_uri = self.encrypt(msg_uri, self.pubkey_b64, KOMRADE_PRIV_KEY)
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
            
        res = await node.get(uri_msg)
        self.log('res = ',res)
        if res is not None:
            double_encrypted_payload_b64 = res
            single_encrypted_payload = self.decrypt(double_encrypted_payload_b64, KOMRADE_PUB_KEY)
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
            from_pubkey_b64_accto_name = tmpP.pubkey_b64
            assert from_pubkey_b64==from_pubkey_b64_accto_name

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














