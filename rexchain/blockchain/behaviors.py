# -*- encoding: utf-8 -*-
'''
    Model behaviors functions that are repit between models
'''
import json
import hashlib
import logging

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.contrib.postgres.fields import JSONField

logger = logging.getLogger('django_info')


class IOBlockchainize(models.Model):
    '''
       Input Output Blockchainize Abstract Model
    '''

    # Time purpose
    timestamp = models.DateTimeField("Datetime object", blank=True, default=timezone.now)

    # For Validate Transaction
    # Filter against this when
    readable = models.BooleanField("Check if data is readable(synonym spent)", default=False, blank=True)
    is_valid = models.BooleanField("Check if signature validation was valid", default=True, blank=True)
    signature = models.TextField("Signature with PK and data transaction ", blank=True, default="")

    # For tracking Inputs and Outputs
    hash_id = models.TextField("Hash for Blockchainize Object", blank=True, default="")
    previous_hash = models.TextField("Previous Hash for Blockchainize Object", blank=True, default="0")

    # Computed data for hashing purpose
    raw_msg = models.TextField("Chaining raw data of Blockchainize object for hashing purpose", blank=True, default="")

    data = JSONField('Raw Data from Payload', blank=True, default={})

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
            json.dumps(self.data).encode() +
            timezone.now().isoformat().encode() +
            self.previous_hash.encode() +
            str(self.is_valid).encode() +
            str(self.readable).encode() +
            self.signature.encode()
        )
        self.raw_msg = str(msg).encode('utf-8')

    def raw_size(self):
        ''' get size of model '''
        _size = (
            self.raw_msg +
            self.hash_id
        )
        return len(_size) * 8

    @cached_property  # noqa: F811
    def raw_size(self):
        # Get the size of the raw rx
        # TODO make improvements here
        _size = (
            json.dumps(self.data) +
            self.timestamp.isoformat()
        )
        return len(_size) * 8

    def transfer_ownership(self):
        ''' These method only appear when Rx is transfer succesfully'''
        self.readable = False
        self.destroy_data()
        self.save()
        logger.info("[TRANSFER_OWNERSHIP]Success destroy data!")

    def destroy_data(self):
        ''' Destroy data if transfer ownership (Adjust Logic if model change) '''
        self.data = [hashlib.sha256(json.dumps(self.data)).hexdigest()]
