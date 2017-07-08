# -*- encoding: utf-8 -*-
# AESCipher
# from core.utils import AESCipher
## Hash lib
import hashlib
from datetime import timedelta, datetime
# Unicode shite
import unicodedata
from django.utils.encoding import python_2_unicode_compatible
import rsa
import md5

# Returns a tuple with Private and Public keys
def get_new_asym_keys():
    return rsa.newkeys(512)

# Encrypt with public key
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
