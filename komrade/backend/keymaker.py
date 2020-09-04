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

    def findkey(self, keyname, keychain={}, uri=None):
        # look in keychain, then in crypt, for this key
        given_key = keychain.get(keyname)
        if given_key: return given_key

        found_key = self.crypt_keys.get(uri,prefix=f'/{keyname}/')
        if found_key: return found_key

    def getkey(self, keyname, keychain={}, uri=None):
        # 1) I already have this key stored in either the keychain or the crypt; return straight away
        key = self.findkey(keyname, keychain, uri)
        if key: return key

        ## 2) I can assemble the key
        key_encr = self.findkey(keyname+'_encr', keychain,uri)
        key_decr_key = self.findkey(keyname+'_decr_key', keychain, uri)
        key_decr_cell = self.findkey(keyname+'_decr_cell', keychain, uri)
        key_decr_pass = self.findkey(keyname+'_decr_pass', keychain, uri)
        key = self.assemble_key(key_encr, key_decr_key, key_decr_cell, key_decr_pass)
        return key

    def assemble_key(self, key_encr, key_decr_key, key_decr_cell, key_decr_pass):
        # need the encrypted half
        if not key_encr:
            self.log('!! encrypted half not given')
            return

        # need some way to regenerate the decryptor
        if not key_decr_cell:
            if key_decr_key:
                key_decr_cell = SCellSeal(key=key_decr_key)
            elif key_decr_pass:
                key_decr_cell = SCellSeal(passphrase=passphrase)
        
        # need the decryptor half
        if not key_decr_cell:
            self.log('!! decryptor half not given')
            return

        # decrypt!
        try:
            key = key_decr_cell.decrypt(key_encr)
            self.log('assembled_key built:',key)
            return key
        except ThemisError as e:
            self.log('!! decryption failed:',e)
        
    
    # def assemble_key(self, key_encr, key_decr, passphrases={}, keychain_encr={}, keychain_decr={}, keyname=''):
        
    #     key_decr_decr_key,key_decr_decr_cell = self.getkey_decr_decr_keycell(passphrases=passphrases,keyname=keyname)
    #     self.log(f'about to decrypt {key_decr_encr} ({keyname}) with cell {key_decr_decr_cell}')
    #     try:
    #         key_decr = key_decr_decr_cell.decrypt(key_decr_encr)
    #     except ThemisError as e:
    #         self.log('!!',e)
    #         return
    #     self.log(f'{keyname}bkey_decr <--',pubkey_decr)
    #     return pubkey_decr

    def buildkey(self, uri, passphrases={}, keychain_encr={}, keychain_decr={}, keyname='pubkey'):
        # if the decryption keys have been provided to me
        key_decr = None
        key_encr = None

        if keychain_decr:
            # get the relevant decryption key
            key_decr = keychain_decr.get(f'{keyname}_decr'):
            
            # see if I have the right encrypted key
            key_encr = self.getkey_encr(uri, keyname=keyname+'_encr', **kwargs)
        
        # conversely, if the encryption keys have been provided to me
        elif keychain_encr:
            # get the relevant encryption key
            key_encr = keychain_encr.get(f'{keyname}_encr'):
            
            # see if I have the right decryption key stored
            key_decr = self.getkey_decr(uri, keyname=keyname, )
        
        # then, once I have both: put them together
        if not key_decr and not key_encr: return 
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



    ## (1-X) ENCRYPTED KEYS
    def getkey_encr(self, uri, passphrases={}, keychain_decr={}, keyname='pub_encr'):
        # can I find the key?
        found_key = self.crypt_keys.get(uri,prefix=f'/{keyname}/')
        if found_key: return found_key
        # otherwise, get it by encrypting its components?
        key_made = self.buildkey_encr(passphrases=passphrases)
        if key_made: return key_made
        # flag error
        self.log(f'!! could not get {keyname}key_encr')
    def pubkey_encr(self, **kwargs):
        return self.getkey_encr(uri=self.name,keyname='pub',**kwargs)
    def privkey_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr(**kargs),keyname='priv',**kwargs)
    def adminkey_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr(**kargs),keyname='admin',**kwargs)
    def buildkey_encr(self, passphrases={}, keyname='pub'):
        # get decrypted key
        key_encr_decr = self.getkey_encr_decr(keyname=keyname)
        # get encrypted key
        key_encr_encr_key,key_encr_encr_cell = self.getkey_encr_encr_keycell(passphrases=passphrases,keyname=keyname)
        self.log(f'about to encrypt {key_encr_decr} ({keyname}) with cell {key_encr_encr_cell}')
        try:
            key_encr = key_encr_encr_cell.encrypt(key_encr_decr)
        except ThemisError as e:
            self.log('!!',e)
            return
        self.log(f'{keyname}bkey_encr <--',pubkey_encr)
        return pubkey_encr


    ### (1-Y) DECRYPTION KEYS
    def getkey_decr(self, uri, passphrases={}, keychain_encr={}, keyname=''):
        # can I find the key?
        found_key = self.crypt_keys.get(uri,prefix=f'/{keyname}_decr/')
        if found_key: return found_key
        # otherwise, get it by decrypting its components?
        key_made = self.buildkey_decr(passphrases=passphrases)
        if key_made: return key_made
        # flag error
        self.log(f'!! could not get {keyname}key_decr')
    def pubkey_decr(self, **kwargs):
        return self.getkey_decr(uri=self.name,keyname='pub',**kwargs)
    def privkey_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr(**kargs),keyname='priv',**kwargs)
    def adminkey_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr(**kargs),keyname='admin',**kwargs)
    def buildkey_decr(self, passphrases={}, keyname='pub'):
        # get encrypted key
        key_decr_encr = self.getkey_decr_encr(keyname=keyname)
        # get decrypted key
        key_decr_decr_key,key_decr_decr_cell = self.getkey_decr_decr_keycell(passphrases=passphrases,keyname=keyname)
        self.log(f'about to decrypt {key_decr_encr} ({keyname}) with cell {key_decr_decr_cell}')
        try:
            key_decr = key_decr_decr_cell.decrypt(key_decr_encr)
        except ThemisError as e:
            self.log('!!',e)
            return
        self.log(f'{keyname}bkey_decr <--',pubkey_decr)
        return pubkey_decr


    ## MAGIC KEY ATTRIBUTES    
    # loading keys back

    ### DECR DECR KEYCELL


    ### DECR ENCR KEYS
    ## Third level: splitting (encrypted/decryption key) the encrypted keys and decryption keys above

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


    def getkey_decr_keycell(self, passphrases={}, keyname='pub_decr_decr_key'):
        # get or make
        decr_key = None
        decr_cell = None

        passphrase=passphrases.get(keyname+'_pass')
        if passphrase:
            decr_key=None
            decr_cell = SCellSeal(passphrase=passphrase)
            return (decr_key,decr_cell)

        # do I have a decryption key stored?
        decr_key = self.crypt_keys.get(self.name,prefix=f'/{keyname}/')
        if decr_key:
            decr_cell = SCellSeal(key=decr_key)
            return (decr_key,decr_cell)

        # otherwise, make a new decryption key and cell
        if not decr_cell:
            return self.genkey_pass_keycell()

        return (decr_key,decr_cell)

    def pubkey_decr_decr_keycell(self,passphrases={}):
        return self.getkey_decr_decr_keycell(passphrase=passphrase, keyname='pub')
    def privkey_decr_decr_keycell(self,passphrases={}):
        return self.getkey_decr_decr_keycell(passphrase=passphrase, keyname='priv')
    def adminkey_decr_decr_keycell(self,passphrases={}):
        return self.getkey_decr_decr_keycell(passphrase=passphrase, keyname='admin')




    ### DECR KEYS

    
