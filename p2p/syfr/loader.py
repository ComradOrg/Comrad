import copy
import hashlib
import os
import requests

from .syfr import *

DATA_BLOCK_SIZE = 65536


def encrypt_file(file_path, rsa_priv, receiver_pubkey):
    contents = open(file_path).read()

    return blocks


def masters_from_children(children, rsa_priv, receiver_pubkey):
    contents = []
    masters_content = []
    last_master_content = "MASTER:"

    for child in children:
        if len(last_master_content) + len(child['id']) > DATA_BLOCK_SIZE - bitsize_marker_length - 32:
            masters_content.append(last_master_content)
            last_master_content = "MASTER:"

        last_master_content += "\n{0}".format(child['id'])

    if len(last_master_content) > 8:
        masters_content.append(last_master_content)

    masters = [encrypt_block(long_pad(master_c), rsa_priv, receiver_pubkey) for master_c in masters_content]
    return masters


def fetch_block(id):
    url = "https://syfr.io/data/v0/{0}".format(id)
    print("Fetching block {0} from {1}.".format(id, url))
    return requests.get(url).content


def tree_decrypt_block(block, priv):
    """
    In parsing a tree, determine if the block is a master block.
    If so, return TRUE and a list of ids.
    Else it is a leaf-content block, return FALSE and whole contents.
    Whole block dict assumed to be passed in.  If ID passed in, try to fetch.
    """

    if isinstance(block, str):
        block = fetch_block(id)

    contents = long_unpad(full_decrypt_block(block, priv))
    if contents[0:7] == "MASTER:":
        return True, contents[7:].split('\n')[1:]
    else:
        return False, contents


def tree_decrypt(block, priv, cached_blocks=None):
    """
    Decrypts and assembles an entire block tree.
    If blocks are provided, checks here for cached blocks, otherwise it fetches
    on Internet.
    """
    content = ""
    cont = True
    blocks = [block]

    if isinstance(cached_blocks, list):
        cb = dict([(b['id'], b) for b in cached_blocks])
        cached_blocks = cb
    level = 0

    while cont:
        new_contents = []
        print("Decrypting {0} blocks at level {1}.".format(len(blocks), level))
        level += 1
        for b in blocks:
            if cached_blocks and isinstance(b, str) and b in cached_blocks:
                new_contents.append(tree_decrypt_block(cached_blocks[b], priv))
            else:
                new_contents.append(tree_decrypt_block(b, priv))

        blocks = []
        for is_master, con in new_contents:
            if not is_master:
                content += con
            else:
                blocks += con
        cont = len(blocks) > 0

    return content


def assemble_block_tree(contents, rsa_priv, receiver_pubkey):
    content_pieces = divide_contents(contents)
    print("Encrypting {0} Leaf Blocks.".format(len(content_pieces)))
    leaf_blocks = [encrypt_block(c, rsa_priv, receiver_pubkey) for c in content_pieces]
    blocks = copy.copy(leaf_blocks)
    n = len(blocks)
    new_blocks = blocks

    while n > 1:
        new_blocks = masters_from_children(new_blocks, rsa_priv, receiver_pubkey)
        print("APPENDING {0} Masters".format(len(new_blocks)))
        blocks += new_blocks
        n = len(new_blocks)

    return blocks


def divide_contents(contents):
    subcontents = []
    n = 0
    while n < len(contents):
        m = min(len(contents), n + DATA_BLOCK_SIZE - bitsize_marker_length)
        subcontent = contents[n:m]
        subcontent = long_pad(subcontent, DATA_BLOCK_SIZE)
        subcontents.append(subcontent)
        n += DATA_BLOCK_SIZE - bitsize_marker_length
    return subcontents


def unite_contents(content_blocks):
    content = ""
    for n, x in enumerate(content_blocks):
        content += long_unpad(x)

    return content


def compute_block_hash(block_dict):
    s = ""
    for k in sorted(block_dict.keys()):
        if k in ['id']:
            continue
        s += "&{0}:{1}".format(k, block_dict[k])
    return hashlib.sha256(s).hexdigest()


def decompose_metadata(metadata):
    sender, receiver = [x.split(':')[-1] for x in metadata.split(';')]
    return sender, receiver


def recompose_metadata(sender, receiver):
    # TODO remove this
    return "sender_pubkey:{0};receiver_pubkey:{1}".format(sender, receiver)


def encrypt_block(content, rsa_priv, receiver_pubkey):
    assert len(content) == DATA_BLOCK_SIZE
    aes_ciphertext, encry_aes_key, hmac, hmac_signature, iv, metadata = \
        encrypt(content, rsa_priv, receiver_pubkey)
    sender, receiver = decompose_metadata(metadata)
    response = {
                'aes_ciphertext': aes_ciphertext,
                'encry_aes_key': encry_aes_key,
                'hmac': hmac,
                'hmac_signature': hmac_signature,
                'iv': iv,
                'sender_public_key': sender,
                'receiver_public_key': receiver
                }
    response['id'] = compute_block_hash(response)
    return response


def full_decrypt_block(response, receiver_privkey):
    assert compute_block_hash(response) == response['id']


    return decrypt(
            response['aes_ciphertext'],
            response['encry_aes_key'],
            response['hmac'],
            response['hmac_signature'],
            receiver_privkey,
            response['iv'],
            recompose_metadata(
                response['sender_public_key'], response['receiver_public_key'])
        )


def aes_decrypt_block(response, aes_key):
    return
