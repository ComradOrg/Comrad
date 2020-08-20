from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import os

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
        str(message).encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

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
def gen_global_keys(fn='.keys.global.json'):
    from kivy.storage.jsonstore import JsonStore

    private_key,public_key=new_keys(save=False,password=None)
    pem_private_key = save_private_key(private_key,password=None,return_instead=True)
    pem_public_key = save_public_key(public_key,return_instead=True)

    store = JsonStore('./.keys.global.json')

    store.put('_keys',private=str(pem_private_key.decode()),public=str(pem_public_key.decode())) #(private_key,password=passkey)

