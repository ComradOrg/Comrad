# internal imports
import os,sys; sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')),'..')))
from komrade import *
from komrade.backend.crypt import *
from komrade.backend.keymaker import *
from komrade.backend.mazes import *
from komrade.backend.switchboard import *




class Operator(Keymaker):
    
    def __init__(self, name, passphrase=None, path_crypt_keys=PATH_CRYPT_CA_KEYS, path_crypt_data=PATH_CRYPT_CA_DATA):
        super().__init__(name=name,passphrase=passphrase, path_crypt_keys=path_crypt_keys, path_crypt_data=path_crypt_data)
        self.boot(create=False)

    def boot(self,create=False):
         # Do I have my keys?
        have_keys = self.exists()
        
        # If not, forge them -- only once!
        if not have_keys and create:
            self.get_new_keys()

        # load keychain into memory
        self._keychain = self.keychain(force = True)

    def encrypt_to_send(self,msg_json,from_privkey,to_pubkey):
        if not msg_json or not from_privkey or not to_pubkey:
            self.log('not enough info!')
            return b''
        msg_b = package_for_transmission(msg_json)
        try:
            msg_encr = SMessage(
                from_privkey,
                to_pubkey,
            ).wrap(msg_b)
            return msg_encr
        except ThemisError as e:
            self.log('unable to encrypt to send!',e)
        return b''

    def decrypt_from_send(self,msg_encr,from_pubkey,to_privkey):
        if not msg_b_encr or not from_privkey or not to_pubkey:
            self.log('not enough info!')
            return b''
        try:
            # decrypt
            msg_b = SMessage(
                to_privkey,
                from_pubkey,
            ).unwrap(msg_b_encr)
            # decode
            msg_json = unpackage_from_transmission(msg_b)
            # return
            return msg_json
        except ThemisError as e:
            self.log('unable to decrypt from send!',e)
        return b''


     def encrypt_outgoing(self,
                          json_phone={},
                          json_caller={},
                          from_phone_privkey=None,
                          from_caller_privkey=None,
                          to_pubkey=None,
                          unencr_header=b''):
        
        # 1) unencrypted header:
        

        # 2) encrypt to phone
        json_phone_encr = self.encrypt_to_send(json_phone,from_phone_privkey,to_pubkey)

        # 3) to caller
        json_caller_encr = self.encrypt_to_send(json_caller,from_caller_privkey,to_pubkey)

        # return
        req_data_encr = unencr_header + BSEP + json_phone_encr + BSEP + json_caller_encr
        return req_data_encr

    def reassemble_nec_keys_using_header(self,unencr_header):
        assert unencr_header.count(BSEP2)==1
        phone_pubkey_decr,op_pubkey_decr = unencr_header.split(BSEP2)
        
        # get phone pubkey
        new_phone_keychain = self.phone.keychain(extra_keys={'pubkey_decr':phone_pubkey_decr},force=True)
        new_op_keychain = self.keychain(extra_keys={'pubkey_decr':op_pubkey_decr},force=True)

        phone_pubkey = new_phone_keychain.get('pubkey')
        op_pubkey = new_op_keychain.get('pubkey')
        return (phone_pubkey,op_pubkey)

    def reassemble_necessary_keys_using_decr_phone_data(self,decr_phone_data):
        name=decr_phone_data.get('name')
        if not name: return None

        try:
            caller = Caller(name)
            self.log('got caller on phone',name,caller)
            return caller.pubkey_
        

        
    def decrypt_incoming(self,
                          json_phone={},
                          json_caller={}):
        # step 1 split:
        data_unencr,data_encr_by_phone,data_encr_by_caller = data.split(BSEP)
        data_unencr_by_phone,data_unencr_by_caller = None,None

        # set up
        DATA = {}

        # assuming the entire message is to me
        to_pubkey = self.pubkey_

        # get other keys from halfkeys
        phone_pubkey,op_pubkey = self.reassemble_nec_keys_using_header(data_unencr)

        # 2) decrypt from phone
        json_phone_decr = self.decrypt_from_send(json_phone,phone_pubkey,self.privkey_)

        # 3) decrypt from caller
        caller_pubkey = self.reassemble_necessary_keys_using_decr_phone_data(json_phone_decr)
        json_caller_encr = self.decrypt_from_send(json_caller,from_caller_privkey,to_pubkey)

        # return
        req_data_encr = unencr_header + BSEP + json_phone_encr + BSEP + json_caller_encr
        return req_data_encr
