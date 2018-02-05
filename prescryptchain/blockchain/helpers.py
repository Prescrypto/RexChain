''' Basic functions and vars for genesis generation '''
import string
import random
import hashlib
import merkletools

def genesis_hash_generator(size=64, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

GENESIS_INIT_DATA = {
    "hashes" : [
        hashlib.sha256("chucho").hexdigest(),
        hashlib.sha256("cheve").hexdigest(),
        hashlib.sha256("bere").hexdigest(),
]}

def get_genesis_merkle_root():
    ''' Get first '''
    _mt = merkletools.MerkleTools()

    for single_hash in GENESIS_INIT_DATA["hashes"]:
        _mt.add_leaf(single_hash)
    _mt.make_tree();
    # get merkle_root and return
    return _mt.get_merkle_root();

