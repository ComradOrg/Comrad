import base64
import hashlib
import math
import os

from . import syfr as crypto
from . import loader


def random_content(pseudolength):
    return base64.b64encode(os.urandom(pseudolength))


def test_divide_unite_contents():
    # random contents
    complexity = loader.DATA_BLOCK_SIZE * 100 # won't create exactly this length
    contents = random_content(complexity)
    size = len(contents)
    subcontents = loader.divide_contents(contents)
    assert len(subcontents) == math.ceil(float(size) / float(loader.DATA_BLOCK_SIZE))
    assert all([len(x) == loader.DATA_BLOCK_SIZE for x in subcontents])

    united = loader.unite_contents(subcontents)
    assert hashlib.sha256(united).hexdigest() == hashlib.sha256(contents).hexdigest()


def test_encrypt_block():
    content = crypto.long_pad(random_content(1000))
    rsa_priv = crypto.generate_rsa_key()
    priv2 = crypto.generate_rsa_key()
    receiver_pubkey = crypto.serialize_pubkey(priv2.public_key())

    response = loader.encrypt_block(content, rsa_priv, receiver_pubkey)
    assert loader.full_decrypt_block(response, priv2) == content


def test_assemble_block_tree():
    contents = random_content(10**6)
    rsa_priv = crypto.generate_rsa_key()
    priv2 = crypto.generate_rsa_key()
    receiver_pubkey = crypto.serialize_pubkey(priv2.public_key())
    blocks = loader.assemble_block_tree(contents, rsa_priv, receiver_pubkey)
    derived_contents = loader.tree_decrypt(blocks[-1], priv2, cached_blocks=blocks)
    assert derived_contents == contents
