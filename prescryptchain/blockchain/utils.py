# -*- encoding: utf-8 -*-
# AESCipher
# from core.utils import AESCipher
## Hash lib
import hashlib
import logging
from datetime import timedelta, datetime
import qrcode
# Unicode shite
import unicodedata
from django.utils.encoding import python_2_unicode_compatible
# FOr signing
import md5
import merkletools
# PoE
from blockcypher import embed_data, get_transaction_details
from django.conf import settings

def calculate_hash(index, previousHash, timestamp, data):
    # Calculate hash
    hash_obj = hashlib.sha256(str(index) + previousHash + str(timestamp) + data)
    return hash_obj.hexdigest()

# Merkle root - gets a list of prescriptions and returns a merkle root
def get_merkle_root(prescriptions):
    # Generate merkle tree
    logger = logging.getLogger('django_info')
    mt = merkletools.MerkleTools() # Default is SHA256
    # Build merkle tree with Rxs
    for rx in prescriptions:
        mt.add_leaf(rx.rxid)
    mt.make_tree();
    # Just to check
    logger.error("Leaf Count: {}".format(mt.get_leaf_count()))
    # get merkle_root and return
    return mt.get_merkle_root();

#  Proves a hash is in merkle root of block merkle tree
def is_rx_in_block(target_rx, block):
    #  We need to create a new tree and follow the path to get this proof
    logger = logging.getLogger('django_info')
    mtn = merkletools.MerkleTools()
    rx_hashes = block.data["hashes"]
    n = 0
    for index, hash in enumerate(rx_hashes):
        mtn.add_leaf(hash)
        if target_rx.rxid == hash:
            n = index
    # Make the tree and get the proof
    mtn.make_tree()
    proof = mtn.get_proof(n)
    logger.error("Proof: {}".format(proof))
    return mtn.validate_proof(proof, target_rx.rxid, block.merkleroot)


def get_qr_code(data, file_path="/tmp/qrcode.jpg"):
    ''' Create a QR Code Image and return it '''
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(file_path)
    with open(file_path, "rb") as f:
        return f.read()

class PoE(object):
    ''' Object tools for encrypt and decrypt info '''
    logger = logging.getLogger('django_info')

    def journal(self, merkle_root):
        try:
            data = embed_data(to_embed=merkle_root, api_key=settings.BLOCKCYPHER_API_TOKEN, coin_symbol=settings.CHAIN)
            if isinstance(data, dict):
                self.logger.info('[PoE data]:{}'.format(data))
                return data.get("hash", "")
            else:
                self.logger.error("Type of data:".format(type(data)))
                return None
        except Exception as e:
            self.logger.error("[PoE ERROR] Error returning hash from embed data, Error :{}, type({})".format(e, type(e)))

    def attest(self, txid):
        try:
            return get_transaction_details(txid, coin_symbol=settings.CHAIN)
        except Exception as e:
            print("[PoE ERROR] Error returning transantion details :%s, type(%s)" % (e, type(e)))
            raise e
