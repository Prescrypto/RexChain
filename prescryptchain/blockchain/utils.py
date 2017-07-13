# -*- encoding: utf-8 -*-
# AESCipher
# from core.utils import AESCipher
## Hash lib
import hashlib
from datetime import timedelta, datetime
import rsa
import cPickle
import binascii
# Unicode shite
import unicodedata
from django.utils.encoding import python_2_unicode_compatible
# FOr signing
import md5
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from base64 import b64decode

# Returns a tuple with Private and Public keys
def get_new_asym_keys():
    return rsa.newkeys(512)

# Give it a key, returns a hex string ready to save
def savify_key(EncryptionPublicKey):
    pickld_key = cPickle.dumps(EncryptionPublicKey)
    return bin2hex(pickld_key)

def calculate_hash(index, previousHash, timestamp, data):
    # Calculate hash
    hash_obj = hashlib.sha256(str(index) + previousHash + str(timestamp) + data)
    return hash_obj.hexdigest()


# Give it a hex saved string, returns a Key object ready to use
def un_savify_key(HexPickldKey):
    bin_str_key = hex2bin(HexPickldKey)
    return cPickle.loads(bin_str_key)

# Encrypt with PublicKey object
def encrypt_with_public_key(message, EncryptionPublicKey):
    encryptedtext=rsa.encrypt(message, EncryptionPublicKey)
    return encryptedtext

# Decrypt with private key
def decrypt_with_private_key(encryptedtext, EncryptionPrivateKey):
    message =rsa.decrypt(encryptedtext, EncryptionPrivateKey)
    return message

# A simple implementation
def test(message):
    print "This is the original message: "+message
    (EncryptionPublicKey, EncryptionPrivateKey) = get_new_asym_keys()
    # Encrypt with public keys
    encryptedtext = encrypt_with_public_key(message, EncryptionPublicKey)
    print "This is the encrypted message: "+encryptedtext
    # Decrypt with private keys
    decrypted_message = decrypt_with_private_key(encryptedtext, EncryptionPrivateKey)
    print "This is the decrypted message: "+decrypted_message


# convert str to hex
# This needs to be used to save the messages and keys
def bin2hex(binStr):
    return binascii.hexlify(binStr)
# convert hex to str
def hex2bin(hexStr):
    return binascii.unhexlify(hexStr)