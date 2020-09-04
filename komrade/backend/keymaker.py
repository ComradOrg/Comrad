class Keymaker(Logger):


    ### BASE STORAGE
    @property
    def crypt_keys(self):
        if not hasattr(self,'_crypt_keys'):
            self._crypt_keys = Crypt(fn=PATH_CRYPT_KEYS)
        return self._crypt_keys

    @property
    def crypt_data(self):
        if not hasattr(self,'_crypt_data'):
            self._crypt_data = Crypt(fn=PATH_CRYPT_DATA)
        return self._crypt_data


    ### STARTING WITH MOST ABSTRACT

    ### (1) Final keys
    def getkey(self, uri, passphrases={}, keychain_encr={}, keychain_decr={}, keyname=''):
        if not keyname: return
        key = None

        # if the decryption keys have been provided to me
        if keychain_decr:
            # get the relevant decryption key
            key_decr = keychain_encr.get(f'{keyname}key_decr'):
            
            # see if I have the right encrypted key
            key_encr = self.getkey_encr(uri, passphrases=passphrases, keychain_decr=keychain_decr, keyname=keyname)
        
        # conversely, if the encryption keys have been provided to me
        elif keychain_encr:
            # get the relevant encryption key
            key_encr = keychain_encr.get(f'{keyname}key_decr'):
            
            # see if I have the right encrypted key
            key_decr = self.getkey_decr(uri, passphrases=passphrases, keychain_decr=keychain_decr, keyname=keyname)
        
        # then, once I have both:
        if not keychain_decr and not keychain_encr: return 
        try:
            key = SCellSeal(key=key_decr).decrypt(key_encr)
        except ThemisError as e:
            self.log('key recovery failed',e)
        return key
    
    def pubkey(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pub',**kwargs)
    def privkey(self, **kwargs):
        return self.getkey(uri=self.pubkey(**kwargs),keyname='priv',**kwargs)
    def adminkey(self, **kwargs):
        return self.getkey(uri=self.privkey(**kwargs),keyname='admin',**kwargs)



    ## (2A) ENCRYPTED KEYS
    def getkey_encr(self, uri, passphrases={}, keychain_decr={}, keyname=''):
        return self.crypt_keys.get(uri,prefix=f'/{keyname}_encr/')
    def pubkey_encr(self, **kwargs):
        return self.getkey_encr(uri=self.name,keyname='pub',**kwargs)
    def privkey_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr(**kargs),keyname='priv',**kwargs)
    def adminkey_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr(**kargs),keyname='admin',**kwargs)


    ### (2B) DECRYPTED KEYS
    def getkey_decr(self, uri, passphrases={}, keychain_encr={}, keyname=''):
        key_loaded = self.crypt_keys.get(uri,prefix=f'/{keyname}_decr/')
        if key_loaded: return key_loaded

        # otherwise, get it by decrypting its components?
        return self.buildkey



    def pubkey_decr(self, **kwargs):
        return self.getkey_decr(uri=self.name,keyname='pub',**kwargs)
    def privkey_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr(**kargs),keyname='priv',**kwargs)
    def adminkey_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr(**kargs),keyname='admin',**kwargs)

    def buildkey_decr(self, passphrases={}, keyname='pub'):
        # need two pieces: its encrypted part and its decrypted part
        key_decr_encr = self.getkey_decr_encr(keyname=keyname)
        
        key_decr_decr_key,pubkey_decr_decr_cell = self.getkey_decr_decr_keycell(passphrase,keyname=keyname)

        self.log(f'about to decrypt {pubkey_decr_encr} with cell {pubkey_decr_decr_cell}')
        try:
            pubkey_decr = pubkey_decr_decr_cell.decrypt(pubkey_decr_encr)
        except ThemisError as e:
            self.log('!!',e)
            exit()
        
        self.log('pubkey_decr <--',pubkey_decr)
        return pubkey_decr

    def pubkey_decr(self, passphrases={}):
        pubkey_decr_encr = self.pubkey_decr_encr()
        pubkey_decr_decr_key,pubkey_decr_decr_cell = self.pubkey_decr_decr_keycell(passphrase)

        self.log(f'about to decrypt {pubkey_decr_encr} with cell {pubkey_decr_decr_cell}')
        try:
            pubkey_decr = pubkey_decr_decr_cell.decrypt(pubkey_decr_encr)
        except ThemisError as e:
            self.log('!!',e)
            exit()
        
        self.log('pubkey_decr <--',pubkey_decr)
        return pubkey_decr

    def privkey_decr(self, passphrases={}):
        privkey_decr_encr = self.privkey_decr_encr()
        privkey_decr_decr_cell = self.privkey_decr_decr_cell(passphrase)
        privkey_decr = privkey_decr_decr_cell.decrypt(privkey_decr_encr)
        return privkey_decr

    def adminkey_decr(self, passphrases={}):
        adminkey_decr_encr = self.adminkey_decr_encr()
        adminkey_decr_decr_cell = self.adminkey_decr_decr_cell(passphrase)
        adminkey_decr = adminkey_decr_decr_cell.decrypt(adminkey_decr_encr)
        return adminkey_decr

    def keychain_decr(self, pubkey_pass = None, privkey_pass = None, adminkey_pass = None):
        return {
            'pubkey_decr':self.pubkey_decr(pubkey_pass),
            'privkey_decr':self.privkey_decr(privkey_pass),
            'adminkey_decr':self.adminkey_decr(adminkey_pass)
        }

    ## MAGIC KEY ATTRIBUTES    
    # loading keys back

    ### DECR DECR KEYCELL

    # Get key de-cryptors
    def genkey_pass_keycell(self,pass_phrase,q_name='Read permissions?'):
        if pass_phrase is None:
            pass_key = GenerateSymmetricKey()
            pass_cell = SCellSeal(key=pass_key)
        else:
            if pass_phrase is True: pass_phrase=getpass.getpass(f'Enter pass phrase [{q_name}]: ')
            pass_key = None
            pass_cell = SCellSeal(passphrase=pass_phrase)

        self.log(f'pass_key [{q_name}] <--',pass_key)
        self.log(f'pass_cell [{q_name}] <--',pass_cell)
        return (pass_key, pass_cell)


    def getkey_decr_decr_keycell(self, passphrases={}, keyname='pub'):
        # get or make
        decr_key = None
        decr_cell = None

        if passphrase:
            decr_key=None
            decr_cell = SCellSeal(passphrase=passphrase)
            return (decr_key,decr_cell)

        # if I have one stored?
        decr_key = self.crypt_keys.get(self.name,prefix=f'/{keyname}_decr_decr_key/')
        if decr_key:
            decr_cell = SCellSeal(key=decr_key)
            return (decr_key,decr_cell)

        # if I need to generate one
        if not decr_cell:
            return self.genkey_pass_keycell()

        return (decr_key,decr_cell)

    def pubkey_decr_decr_keycell(self,passphrases={}):
        return self.getkey_decr_decr_keycell(passphrase=passphrase, keyname='pub')
    def privkey_decr_decr_keycell(self,passphrases={}):
        return self.getkey_decr_decr_keycell(passphrase=passphrase, keyname='priv')
    def adminkey_decr_decr_keycell(self,passphrases={}):
        return self.getkey_decr_decr_keycell(passphrase=passphrase, keyname='admin')



    ### DECR ENCR KEYS
    def getkey_decr_encr(self,crypt_key = None,keyname='pub'):
        if not crypt_key: crypt_key = self.name
        key_decr_encr = self.crypt_keys.get(self.name,prefix=f'/{keyname}_decr_encr/')
        self.log(f'{keyname}key_decr_encr <--',key_decr_encr)
        return key_decr_encr
    def pubkey_decr_encr(self,passphrases={}):
        return self.getkey_decr_encr(crypt_key=self.name, keyname='pub')
    def privkey_decr_encr(self,passphrases={}):
        pubkey_decr = self.pubkey_decr(passphrase=passphrase)
        return self.getkey_decr_encr(crypt_key=pubkey_decr, keyname='priv')
    def adminkey_decr_encr(self,passphrases={}):
        privkey_decr=self.privkey_decr(passphrase=passphrase)
        return self.getkey_decr_encr(crypt_key=privkey_decr, keyname='admin')
    


    ### DECR KEYS

    
