from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import os
try:
    from .syfr import * #import syfr
except ImportError:
    from syfr import *

key_dir = os.path.join(os.path.expanduser('~'),'.keys','komrade')
if not os.path.exists(key_dir): os.makedirs(key_dir)
PATH_PRIVATE_KEY=os.path.join(key_dir,'private_key.pem')
PATH_PUBLIC_KEY=os.path.join(key_dir,'public_key.pem')


### CREATING KEYS

def new_keys(save=True,password=None):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    if save:
        save_private_key(private_key,password=password)
        save_public_key(public_key)

    return private_key,public_key



def save_private_key(private_key,fn=PATH_PRIVATE_KEY,password=None, return_instead=False):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption() if not password else serialization.BestAvailableEncryption(password.encode())
    )
    if return_instead: return pem
    with open(fn,'wb') as f: f.write(pem)

def save_public_key(public_key,fn=PATH_PUBLIC_KEY,return_instead=False):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    if return_instead: return pem
    with open(fn,'wb') as f: f.write(pem)



### LOADING KEYS
def load_keys():
    return (load_private_key_from_file(), load_public_key_from_file())

def load_private_key(pem,password=None):
    return serialization.load_pem_private_key(
        pem,
        password=password.encode() if password else None,
        backend=default_backend()
    )

def load_private_key_from_file(fn=PATH_PRIVATE_KEY,password=None):
    with open(fn, "rb") as key_file:
        return load_private_key(key_file.read(), password)

def load_public_key(pem):
    return serialization.load_pem_public_key(
            pem,
            backend=default_backend()
        )

def load_public_key_from_file(fn=PATH_PUBLIC_KEY):
    with open(fn, "rb") as key_file:
        return load_public_key(key_file.read())

### DE/ENCRYPTING
def encrypt_msg(message, public_key):
    return public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def encrypt_msg_symmetric(message):
    import os
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    backend = default_backend()
    key = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    
    ct = encryptor.update(message) + encryptor.finalize()
    return ct
    
def decrypt_msg_symmetric():
    import os
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    backend = default_backend()
    key = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)

    return ct
    decryptor = cipher.decryptor()
    decryptor.update(ct) + decryptor.finalize()
    b'a secret message'

def decrypt_msg(encrypted, private_key):
    return private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

### SIGNING/VERIFYING
def sign_msg(message, private_key):
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def verify_msg(message, signature, public_key):
    try:
        verified = public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    return None




# #private_key,public_key = new_keys()
# private_key,public_key = load_keys()

# #print(private_key)
# #print(public_key)


# #enc = encrypt_msg('Drive your plow over the bones of the dead', public_key)
# #print(enc)

# dec = decrypt_msg(enc,private_key)
# #print(dec)

# msg = b'hello'
# signature = sign_msg(msg,private_key)

# #print(encrypt_msg(b'hello',public_key))

# print(verify_msg(msg+b'!!',signature,public_key))



## ONLY NEEDS RUN ONCE!
def gen_global_keys1(fn='.keys.global.json'):
    from kivy.storage.jsonstore import JsonStore

    private_key,public_key=new_keys(save=False,password=None)
    pem_private_key = save_private_key(private_key,password=None,return_instead=True)
    pem_public_key = save_public_key(public_key,return_instead=True)

    store = JsonStore('./.keys.global.json')

    store.put('_keys',private=str(pem_private_key.decode()),public=str(pem_public_key.decode())) #(private_key,password=passkey)

def gen_global_keys(fn='.keys.global.json'):
    from kivy.storage.jsonstore import JsonStore

    store = JsonStore('./.keys.global.json')

    #store.put('_keys',private=str(pem_private_key.decode()),public=str(pem_public_key.decode())) #(private_key,password=passkey)

    private_key = generate_rsa_key()
    pem_private_key = serialize_privkey(private_key, password=None)# save_private_key(private_key,password=passkey,return_instead=True)
    pem_public_key = serialize_pubkey(private_key.public_key())
    store.put('_keys',private=pem_private_key.decode(),public=pem_public_key.decode()) #(private_key,password=passkey)

"""
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
backend = default_backend()
key = os.urandom(32)
iv = os.urandom(16)
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
encryptor = cipher.encryptor()
ct = encryptor.update(b"a secret message") + encryptor.finalize()
decryptor = cipher.decryptor()
decryptor.update(ct) + decryptor.finalize()
b'a secret message'"""






def aes_rsa_encrypt(message, recipient_rsa_pub):
    aes_key = create_aes_key()
    aes_ciphertext, iv = aes_encrypt(message, aes_key)
    encry_aes_key = rsa_encrypt(aes_key, recipient_rsa_pub)
    return aes_ciphertext, encry_aes_key, iv #, sign


def aes_rsa_decrypt(aes_ciphertext, rsa_priv, encry_aes_key, iv): #, hmac, hmac_signature, rsa_priv, iv, metadata):
    aes_key = rsa_decrypt(encry_aes_key, rsa_priv)
    plaintext = aes_decrypt(aes_ciphertext, aes_key, iv)
    return plaintext




# def _decrypt_rsa(x,privkey=CORRECT_PRIV_KEY):
#     x_decr = rsa_decrypt(x,privkey)
#     return x_decr





    # encrypt sender
    #def _enc_sender(x):
    #    recv=receiver_pubkey

    # encrypt recipient too?

        

    # sender_pubkey_b_encr = sep2.join(
    #     aes_rsa_encrypt(
    #         serialize_pubkey(self.public_key), receiver_pubkey
    #     )
    # )

    # receiver_pubkey_b_encr = sep2.join(
    #     aes_rsa_encrypt(
    #         serialize_pubkey(receiver_pubkey_b, receiver_pubkey
    #     )
    # )
    
    

    # msg_encr = sep2.join([val_encr,val_encr_key,iv])
    # sender_encr = sep2.join(
    #     aes_rsa_encrypt(
    #         serialize_pubkey(self.public_key), receiver_pubkey
    #     )
    # )
    # signature_encr = sep2.join(
    #     rsa_encrypt(
    #     signature,
    #     receiver_pubkey
    # )
    # )
    
    

    # sender = sep2.join(sender_pubkey_b, signature)

    # WDV = sep.join([
    #     time_b,
    #     receiver_encr,
    #     msg_encr,
    #     sender_encr,
    #     signature_encr
    # ])