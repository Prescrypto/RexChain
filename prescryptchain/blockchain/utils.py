# -*- encoding: utf-8 -*-
# AESCipher
from core.utils import AESCipher
## Hash lib
import hashlib
from datetime import timedelta, datetime
# Unicode shite
import unicodedata
from django.utils.encoding import python_2_unicode_compatible
import rsa

# User A
(AEncryptionPublicKey, AEncryptionPrivateKey) = rsa.newkeys(512)
(ASigningPrivateKey, ASigningPublicKey) = rsa.newkeys(512)

# User B
(BEncryptionPublicKey, BEncryptionPrivateKey) = rsa.newkeys(512)
(BSigningPrivateKey, BSigningPublicKey) = rsa.newkeys(512)

# Encrypt with public keys
cleartext="This is a name that no one can know"
print cleartext
encryptedtext=rsa.encrypt(cleartext, BEncryptionPublicKey)
sentmessage=(encryptedtext)
print sentmessage

# Decrypt with private keys
receivedmessage=sentmessage # received message is the sentmessage from above
receivedencryptedtext=(receivedmessage)
receivedcleartext=rsa.decrypt(receivedencryptedtext, BEncryptionPrivateKey)

print receivedcleartext

# Helpful example
def encrypt(self, signatures):
    # Encrypt the hash, using AES
    # Receives signatures array
    message = self.hash
    for sign in signatures:
        AEScipher = AESCipher(sign["hash"])
        message = AEScipher.encrypt(message)
    self.signature = message

def decrypt(self):
    # Returns the signature hash
    message = self.signature
    signatures = self.signatures.all()
    for sign in signatures[::-1]:
        AEScipher = AESCipher(sign.hash) # Accesing Signature property
        message = AEScipher.decrypt(message)
    return message