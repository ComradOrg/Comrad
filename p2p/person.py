import os
from pythemis.skeygen import KEY_PAIR_TYPE, GenerateKeyPair
from pythemis.smessage import SMessage, ssign, sverify
from pythemis.exception import ThemisError
from base64 import b64decode,b64encode

KEY_PATH = os.path.join(os.path.expanduser('~'),'.komrade')

class Person(object):

    def __init__(self,name,api):
        self.name=name
        self.api=api

        self.privkey=None
        self.pubkey=None

        # self.load_or_gen()

    @property
    def key_path_pub(self):
        return os.path.join(KEY_PATH,'.komrade.'+self.name+'.addr')

    @property
    def key_path_priv(self):
        return os.path.join(KEY_PATH,'.komrade.'+self.name+'.key')
        
    @property
    def privkey_b64(self):
        return b64encode(self.privkey)

    @property
    def pubkey_b64(self):
        return b64encode(self.pubkey)
    ## genearating keys
    
    def gen_key(self):
        keypair = GenerateKeyPair(KEY_PAIR_TYPE.EC)
        self.privkey = keypair.export_private_key()
        self.pubkey = keypair.export_public_key()

        with open(self.key_path_priv, "wb") as private_key_file:
            private_key_file.write(self.privkey_b64)

        with open(self.key_path_pub, "wb") as public_key_file:
            public_key_file.write(self.pubkey_b64)


    ## loading keys from disk

    def load_key(self):
        if os.path.exists(self.key_path_pub):
            with open(self.key_path_pub) as pub_f:
                self.pubkey=b64decode(pub_f.read())

        if os.path.exists(self.key_path_priv):
            with open(self.key_path_priv) as priv_f:
                self.privkey=b64decode(priv_f.read())

    def load_or_gen(self):
        self.load_key()
        if not self.pubkey:
            self.gen_key(passphrase)

    def encrypt(self,msg,for_pubkey_b64):
        # handle verification failure
        for_pubkey = b64decode(for_pubkey_b64)
        encrypted_msg = SMessage(self.privkey, for_pubkey).wrap(msg)
        return encrypted_msg

    def decrypt(self,encrypted_msg,from_pubkey_b64):
        # handle verification failure
        from_pubkey = b64decode(from_pubkey_b64)
        decrypted_msg = SMessage(self.privkey, from_pubkey).unwrap(encrypted_msg)

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
    



    
    ## PERSONS
    async def find_pubkey(self,username):
        return await self.api.get('/pubkey/'+username,decode_data=False)

    async def set_pubkey(self): #,username),pem_public_key):
        
        await self.set('/pubkey/'+self.name,self.public_key,encode_data=False)
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

if __name__=='__main__':
    from p2p import Api
    api = Api()
    marx = Person('marx',api=api) #,'marx@marxzuckerburg.com',passphrase='twig')

    marx.gen_key()

    elon = Person('elon',api=api) #,'elon@marxzuckerburg.com',passphrase='twig')
    elon.gen_key()


    msg = b'My public key is '+marx.pubkey_b64
    signed_msg = marx.sign(msg)

    print(msg)
    print(signed_msg)

    verified_msg = elon.verify(signed_msg, marx.pubkey_b64)
    print('verified?',verified_msg)