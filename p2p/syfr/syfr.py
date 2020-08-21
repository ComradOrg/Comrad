import base64
import hashlib
import os

import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.padding import PKCS7

from . import loader

bitsize_marker_length = 10


def generate_rsa_key(complexity=4096):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=complexity,
        backend=default_backend()
     )
    return private_key


def serialize_privkey(key, password=False):
    return base64.b64encode(key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()  if not password else serialization.BestAvailableEncryption(password.encode())
    ))


def serialize_pubkey(pubkey):
    return base64.b64encode(pubkey.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))


def load_pubkey(pubkey_text):
    return serialization.load_der_public_key(
        base64.b64decode(pubkey_text),
        backend=default_backend())


def load_privkey(privkey_text,password=None):
    return serialization.load_der_private_key(
        base64.b64decode(privkey_text),
        password=password.encode() if password else None,
        backend=default_backend()
    )

def load_privkey_fn(fn_privkey,password=None):
    with open(fn_privkey,'rb') as f:
        privkey=load_privkey(f.read(),password=password)

def load_pubkey_fn(fn_pubkey):
    with open(fn_pubkey,'rb') as f:
        privkey=load_pubkey(f.read())

def write_key(key, file_path='mykey.pem'):
    with open(file_path, 'w+') as fh:
        fh.write(key)

def write_key_b(key, file_path='mykey.pem'):
    with open(file_path, 'wb') as fh:
        fh.write(key)


def sign(message, private_key):
    signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
    # signer.update(message)
    return base64.b64encode(signature) #signer.finalize())


def verify_signature(signature, message, pubkey):
    try:
        verified = pubkey.verify(
            base64.b64decode(signature),
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except cryptography.exceptions.InvalidSignature as e:
        print('!?',e)
        return False
    return None
    # verifier.update(message)
    # try:
    #     verifier.verify()
    #     return True
    # except cryptography.exceptions.InvalidSignature:
    #     print("Invalid Signature")
    #     return False


def rsa_encrypt(message, pubkey):
    ciphertext = pubkey.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()), # SHA1 is suspect
            algorithm=hashes.SHA1(),
            label=None
        )
    )
    return base64.b64encode(ciphertext)


def rsa_decrypt(ciphertext, key):
    plaintext = key.decrypt(
        base64.b64decode(ciphertext),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )
    return plaintext


def create_aes_key(complexity=32):
    return base64.b64encode(os.urandom(complexity))


def create_hmac(key, message_list):
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    message = "?".join([str(x) for x in message_list])
    h.update(message)
    return base64.b64encode(h.finalize())


def pad(message, blocksize=128):
    padder = PKCS7(blocksize).padder()
    padded_data = padder.update(message)
    padded_data += padder.finalize()
    return padded_data


def long_pad(message, goal_length=loader.DATA_BLOCK_SIZE):
    assert len(message) + bitsize_marker_length <= goal_length
    c = 0
    for _ in range(goal_length - len(message) - bitsize_marker_length):
        message += "0"
        c += 1
    d = str(c).zfill(bitsize_marker_length)
    message += d
    return message


def unpad(padded_data, blocksize=128):
    unpadder = PKCS7(blocksize).unpadder()
    data = unpadder.update(padded_data)
    return data + unpadder.finalize()


def long_unpad(message):
    assert len(message) <= 10**bitsize_marker_length
    padding_size = int(message[-bitsize_marker_length:])
    return message[0:-bitsize_marker_length-padding_size]


def aes_encrypt(message, key):
    iv = os.urandom(16)
    cipher = Cipher(
            algorithms.AES(base64.b64decode(key)),
            modes.CBC(iv),
            backend=default_backend()
        )
    message = pad(message)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message) + encryptor.finalize()
    return base64.b64encode(ciphertext), base64.b64encode(iv)


def aes_decrypt(ciphertext, key, iv):
    cipher = Cipher(
            algorithms.AES(base64.b64decode(key)),
            modes.CBC(base64.b64decode(iv)),
            backend=default_backend()
        )
    decryptor = cipher.decryptor()
    padded = decryptor.update(base64.b64decode(ciphertext)) + decryptor.finalize()
    return unpad(padded)


def aes_rsa_encrypt(message, recipient_rsa_pub):
    aes_key = create_aes_key()
    aes_ciphertext, iv = aes_encrypt(message, aes_key)
    # hmac_key = hashlib.sha256(aes_key).hexdigest()

    #sender_pubkey = serialize_pubkey(rsa_priv.public_key())
    # recipient_rsa_pub = load_pubkey(receiver_pubkey)
    #recipient_rsa_pub = receiver_pubkey
    # metadata = loader.recompose_metadata(sender_pubkey, receiver_pubkey)

    encry_aes_key = rsa_encrypt(aes_key, recipient_rsa_pub)

    # hmac_list = [metadata, iv, aes_ciphertext, encry_aes_key]
    # hmac = create_hmac(hmac_key, hmac_list)
    # hmac_signature = sign(hmac, rsa_priv)

    # return aes_ciphertext, encry_aes_key, hmac, hmac_signature, iv, metadata
    return aes_ciphertext, encry_aes_key, iv #, sign


def aes_rsa_decrypt(aes_ciphertext, encry_aes_key, iv, rsa_priv): #, hmac, hmac_signature, rsa_priv, iv, metadata):
    aes_key = rsa_decrypt(encry_aes_key, rsa_priv)

    # hmac_key = hashlib.sha256(aes_key).hexdigest()
    # hmac_list = [metadata, iv, aes_ciphertext, encry_aes_key]
    # independent_hmac = create_hmac(hmac_key, hmac_list)
    # assert hmac == independent_hmac

    # sender_pub, receiver_pub = [x.split(':')[-1] for x in metadata.split(';')]
    # sender_pub = load_pubkey(sender_pub)
    #assert verify_signature(hmac_signature, hmac, sender_pub)

    plaintext = aes_decrypt(aes_ciphertext, aes_key, iv)
    return plaintext
