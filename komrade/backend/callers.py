import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend import *

class Caller(Operator):
    """
    Variant of an Operator which handles local keys and keymaking.
    """

    @property
    def phone(self):
        """
        Operator on the line.
        """
        if not hasattr(self,'_phone'):
            self._phone = TheTelephone(caller = self)
        return self._phone

    def get_new_keys(self,pubkey_pass = None, privkey_pass = None, adminkey_pass = None):
        """
        This is the local caller's version.
        He never touches the encrypted keys. Only the Operator does!
        """

        # Get decryptor keys back from The Operator (one half of the Keymaker)
        keychain = self.forge_new_keys(self.name)
        self.log('create_keys() res from Operator? <-',keychain)

        # Now lock the decryptor keys away, sealing it with a password of memory!
        self.lock_new_keys(keychain)

    async def forge_new_keys(self, name = None, pubkey_is_public=False):
        if not name: name=self.name
        if not name: return

        req_json = {'_route':'forge_new_keys','name':name}
        req_json['keys_to_save']=['pubkey_encr','privkey_encr','adminkey_encr']
        req_json['keys_to_return']=['pubkey_decr',
                                    'privkey_decr_encr', 'privkey_decr_decr',
                                    'adminkey_decr_encr', 'adminkey_decr_decr']

        try:
            return await self.phone.req(json_coming_from_phone = req_json)
        except TypeError:
            return None