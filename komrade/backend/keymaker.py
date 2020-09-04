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


    # Concrete keys
    ## (1) Final keys
    def pubkey(self, **kwargs):
        return self.getkey(keyname='pubkey',uri=self.name,**kwargs)
    def privkey(self, **kwargs):
        return self.getkey(keyname='privkey',uri=self.pubkey(**kwargs),**kwargs)
    def adminkey(self, **kwargs):
        return self.getkey(keyname='adminkey',uri=self.privkey(**kwargs),**kwargs)
    
    ## (1-X) Encrypted halves
    def pubkey_encr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_encr',**kwargs)
    def privkey_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr(**kargs),keyname='privkey_encr',**kwargs)
    def adminkey_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr(**kargs),keyname='adminkey_encr',**kwargs)

    ## (1-Y) Decrpytor halves
    def pubkey_decr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_decr',**kwargs)
    def privkey_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr(**kargs),keyname='privkey_decr',**kwargs)
    def adminkey_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr(**kargs),keyname='adminkey_decr',**kwargs)

    ## Second halving!
    ## (1-X-X)
    def pubkey_encr_encr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_encr_encr',**kwargs)
    def privkey_encr_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr_encr(**kargs),keyname='privkey_encr_encr',**kwargs)
    def adminkey_encr_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr_encr(**kargs),keyname='adminkey_encr_encr',**kwargs)

    ## (1-X-Y)
    def pubkey_encr_decr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_encr_decr',**kwargs)
    def privkey_encr_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_encr_decr(**kargs),keyname='privkey_encr_decr',**kwargs)
    def adminkey_encr_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_encr_decr(**kargs),keyname='adminkey_encr_decr',**kwargs)

    ## (1-Y-X)
    def pubkey_decr_encr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_decr_encr',**kwargs)
    def privkey_decr_encr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr_encr(**kargs),keyname='privkey_decr_encr',**kwargs)
    def adminkey_decr_encr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr_encr(**kargs),keyname='adminkey_decr_encr',**kwargs)

    ## (1-Y-Y)
    def pubkey_decr_decr(self, **kwargs):
        return self.getkey(uri=self.name,keyname='pubkey_decr_decr',**kwargs)
    def privkey_decr_decr(self, **kwargs):
        return self.getkey(uri=self.pubkey_decr_decr(**kargs),keyname='privkey_decr_decr',**kwargs)
    def adminkey_decr_decr(self, **kwargs):
        return self.getkey(uri=self.privkey_decr_decr(**kargs),keyname='adminkey_decr_decr',**kwargs)

    ### DECR ENCR KEYS
    ## Third level: splitting (encrypted/decryption key) the encrypted keys and decryption keys above

    

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

