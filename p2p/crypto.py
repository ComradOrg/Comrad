from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os

key_dir = os.path.join(os.path.expanduser('~'),'.keys','komrade')
if not os.path.exists(key_dir): os.makedirs(key_dir)
PATH_PRIVATE_KEY=os.path.join(key_dir,'private_key.pem')
PATH_PUBLIC_KEY=os.path.join(key_dir,'public_key.pem')


### CREATING KEYS

def new_keys(save=True):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    if save:
        save_private_key(private_key)
        save_public_key(public_key)

    return private_key,public_key

def save_private_key(private_key,fn=PATH_PRIVATE_KEY):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(fn,'wb') as f: f.write(pem)

def save_public_key(public_key,fn=PATH_PUBLIC_KEY):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(fn,'wb') as f: f.write(pem)



### LOADING KEYS
def load_keys():
    return (load_private_key(), load_public_key())

def load_private_key(fn=PATH_PRIVATE_KEY):
    with open(fn, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
        

def load_public_key(fn=PATH_PUBLIC_KEY):
    with open(fn, "rb") as key_file:
        return serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

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
    return public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )




#private_key,public_key = new_keys()
private_key,public_key = load_keys()

#print(private_key)
#print(public_key)


enc = encrypt_msg('Drive your plow over the bones of the dead', public_key)
#print(enc)

dec = decrypt_msg(enc,private_key)
#print(dec)

msg = b'hello'
signature = sign_msg(msg,private_key)

#print(encrypt_msg(b'hello',public_key))

print(verify_msg(msg+b'!!',signature,public_key))