# -*- encoding: utf-8 -*-
'''
    Model behaviors functions that are repit between models
'''
import json
import hashlib

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


class IOBlockchainize(models.Model):
    '''
       Input Output Blockchainize Abstract Model
    '''
    # Owner track
    public_key = models.TextField("An Hex representation of Public Key Object", blank=True, default=True)

    # Time purpose
    timestamp = models.DateTimeField("Datetime object",blank=True, default=timezone.now)

    # For Validate Transaction
    readable = models.BooleanField("Check if data is readable(synonym spent)", default=False, blank=True) # Filter against this when
    is_valid = models.BooleanField("Check if signature validation was valid", default=True, blank=True)

    # For tracking Inputs and Outputs
    hash_id = models.TextField("Hash for Blockchainize Object", blank=True, default="")
    previous_hash = models.TextField("Previous Hash for Blockchainize Object", blank=True, default="0")

    # Computed data for hashing purpose
    raw_msg = models.TextField("Chaining raw data of Blockchainize object for hashing purpose", blank=True, default="")

    data = JSONField('Raw Data from Payload', blank=True, default={})

    signature = models.TextField("Signature for the IO/Script", blank=True, default="")

    class Meta:
        abstract = True


    def hash(self):
        ''' Hashes msg_html with utf-8 encoding, saves this in and hash in _signature '''
        hash_object = hashlib.sha256(self.raw_msg)
        self.hash_id = hash_object.hexdigest()

    def create_raw_msg(self):
        ''' Create raw html and encode '''
        msg = (
            self.public_key +
            json.dumps(self.data) +
            timezone.now().isoformat() +
            self.previous_hash +
            str(self.is_valid) +
            str(self.readable) +
            self.signature
        )
        self.raw_msg = msg.encode('utf-8')


    def raw_size(self):
        ''' get size of model '''
        _size = (
            self.raw_msg +
            self.hash_id
        )
        return len(size) * 8


