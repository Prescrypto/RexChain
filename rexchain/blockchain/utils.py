# -*- encoding: utf-8 -*-
# Hash lib
import hashlib
import logging
import merkletools
import requests
import qrcode

from Crypto.PublicKey import RSA
# PoE
from blockcypher import embed_data, get_transaction_details
from core.helpers import create_jira_issue
from django.conf import settings
from collections import OrderedDict


def calculate_hash(index, previousHash, timestamp, data):
    # Calculate hash
    hash_obj = hashlib.sha256(
                    str(index).encode() + previousHash.encode() + str(timestamp).encode() + data.encode())

    return hash_obj.hexdigest()


# Merkle root - gets a list of prescriptions and returns a merkle root
def get_merkle_root(transantions):
    # Generate merkle tree
    logger = logging.getLogger('django_info')
    mt = merkletools.MerkleTools()  # Default is SHA256
    # Build merkle tree with Rxs
    for tx in transantions:
        mt.add_leaf(tx.txid)
    mt.make_tree()
    # Just to check
    logger.error("Leaf Count: {}".format(mt.get_leaf_count()))
    # get merkle_root and return
    return mt.get_merkle_root()


# Proves a hash is in merkle root of block merkle tree
def is_rx_in_block(target_rx, block):
    # We need to create a new tree and follow the path to get this proof
    logger = logging.getLogger('django_info')
    mtn = merkletools.MerkleTools()
    rx_hashes = block.data["hashes"]
    n = 0
    for index, hash in enumerate(rx_hashes):
        mtn.add_leaf(hash)
        if target_rx.transaction.txid == hash:
            n = index
    # Make the tree and get the proof
    mtn.make_tree()
    proof = mtn.get_proof(n)
    logger.error("Proof: {}".format(proof))
    return mtn.validate_proof(proof, target_rx.transaction.txid, block.merkleroot)


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

    def __init__(self, *args, **kwargs):
        '''Global Variables'''
        self.logger = logging.getLogger('django_info')
        self.client_id = settings.STAMPD_ID
        self.secret_key = settings.STAMPD_KEY
        self.blockchain = settings.CHAIN
        self.api_url_base = 'https://stampd.io/api/v2'

    def login_stampd_API(self):
        '''This method is for logging in to the Stampd API service'''
        try:
            login_request = requests.get(
                self.api_url_base + '/init?client_id=' +
                self.client_id + '&secret_key=' + self.secret_key
            )
            login_json = login_request.json()
            if not isinstance(login_json, dict):
                return None

            if login_json.get('code', 500) == 300:
                return login_json
            else:
                self.logger.error("[PoE ERROR] Login FAILED")
                return None
        except Exception as e:
            self.logger.error(
                "[PoE ERROR] Login in STAMPD FAILED: {}, type({})".format(e, type(e)))
            return None

    def journal(self, merkle_root):
        '''This method is for stamp a merkle root in Dash Blockchain'''
        login_json = self.login_stampd_API()
        if login_json is not None:
            # Post a merkle root
            try:
                post_request = requests.post(
                    self.api_url_base + '/hash',
                    data={
                        'sess_id': login_json['session_id'],
                        'blockchain': self.blockchain,
                        'hash': merkle_root,
                    })
                post_json = post_request.json()
                if not isinstance(post_json, dict):
                    return False

                if post_json['code'] == 301:
                    self.logger.info(
                        "[PoE Success] Post Successfully: {}".format(post_json['code']))
                    return True

                elif post_json['code'] == 202:
                    self.logger.info(
                        "[PoE Success] Hash already stamped: {}".format(post_json['code']))
                    return True

                elif post_json['code'] == 106:
                    self.logger.info(
                        "[PoE ERROR] Post FAILED: {}".format(post_json['code']))
                    create_jira_issue(
                        summary="Tickets of Stampd Finished",
                        description="Is necessary to buy more Stampd Tickets for make correctly PoE"
                    )
                    return False

                else:
                    self.logger.error(
                        "[PoE ERROR] Post FAILED : {}".format(post_json['code']))
                    return False

            except Exception as e:
                self.logger.error(
                    "[PoE ERROR] Error to make POST: {}, type({})".format(e, type(e)))
                return False

        else:
            return False

    def attest(self, merkle_root):
        '''This method try get a tx_id of Dash Blockchain'''
        login_json = self.login_stampd_API()
        error_found = {"code": "500"}
        if login_json is not None:
            try:
                get_request = requests.get(
                    '{}/hash?hash={}&blockchain={}&sess_id={}'.format(
                        self.api_url_base,
                        merkle_root,
                        self.blockchain,
                        login_json['session_id']))
                get_json = get_request.json()
                if isinstance(get_json, dict):
                    return get_json
                else:
                    return error_found
            except Exception as e:
                self.logger.error(
                    "[PoE ERROR] Error returning transantion details :{}, type({})".format(e, type(e)))
                return error_found
        else:
            return error_found

    def _journal(self, merkle_root):
        try:
            data = embed_data(
                to_embed=merkle_root, api_key=settings.BLOCKCYPHER_API_TOKEN, coin_symbol=settings.CHAIN)
            if isinstance(data, dict):
                self.logger.info('[PoE data]:{}'.format(data))
                return data.get("hash", "")
            else:
                self.logger.error("Type of data:".format(type(data)))
                return None
        except Exception as e:
            _message_error = "[PoE ERROR] Error returning hash from embed data, Error :{}, Type: {}"
            self.logger.error(_message_error.format(e, type(e)))

    def _attest(self, txid):
        try:
            return get_transaction_details(txid, coin_symbol=settings.CHAIN)
        except Exception as e:
            self.logger.error(
                "[PoE ERROR] Error returning transantion details :{}, type({})".format(e, type(e)))
            raise e


def pubkey_string_to_rsa(string_key):
    '''Take a public key created with jsencrypt and convert it into
    a rsa data of python'''

    with open('pubkey.pem', 'wb') as file:
        file.write(string_key.encode())

    with open('pubkey.pem', 'rb') as file:
        pub_key = file.read()

    pubkey = RSA.importKey(pub_key)
    # Data is rsa type
    return pubkey


def pubkey_base64_from_uri(base64_key):
    ''' Get pub_key from base64 uri '''
    return base64_key.replace(" ", "+")


def pubkey_base64_to_rsa(base64_key):
    ''' Convert base64 pub key to pem file and then pub key rsa object '''
    LINE_SIZE = 64
    BEGIN_LINE = "-----BEGIN PUBLIC KEY-----"
    END_LINE = "-----END PUBLIC KEY-----"

    # Replace spaces with plus string, who is remove it when django gets from
    # uri param
    base64_key.replace(" ", "+")

    lines = [base64_key[i:i + LINE_SIZE]
             for i in range(0, len(base64_key), LINE_SIZE)]

    raw_key = "{}\n".format(BEGIN_LINE)
    for line in lines:
        # iter lines and create s unique string with \n
        raw_key += "{}\n".format(line)

    raw_key += "{}".format(END_LINE)

    return pubkey_string_to_rsa(raw_key), raw_key


def ordered_data(data):
    ''' This method order a variable if is a dictionary if not return the same variable '''
    logger = logging.getLogger('django_info')

    if data is None:
        return data

    if isinstance(data, str):
        return data

    if isinstance(data, list):
        _new_list = []
        for item in data:
            _new_list.append(OrderedDict(
                sorted(item.items(), key=lambda x: x[0])))
        return _new_list

    else:
        _new_dict = {}
        try:
            _new_dict = OrderedDict(sorted(data.items(), key=lambda x: x[0]))
        except Exception as e:
            logger.error(
                "[ordered data ERROR]: {}, type:{}".format(e, type(e)))
            return data

        return _new_dict


def iterate_and_order_json(json_data):
    '''iterates over a json to order all the sub jsons and lists'''
    logger = logging.getLogger('django_info')
    temp_dict = dict()

    if not json_data or not isinstance(json_data, dict):
        return json_data
    try:
        for key, val in json_data.items():
            temp_dict[key] = ordered_data(val)
    except Exception as e:
        logger.error(
            "[iterate_and_order_json ERROR]: {}, type:{}".format(e, type(e)))
        return json_data

    return temp_dict
