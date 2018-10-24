# -*- encoding: utf-8 -*-
# Python Libs
## Hash lib
import hashlib
import base64
import logging
# Date
from datetime import timedelta, datetime
from operator import itemgetter
# Unicode shite
import unicodedata
# Django Libs
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.dateformat import DateFormat

# Our methods
from core.behaviors import Timestampable
from .behaviors import IOBlockchainize
from .managers import (
    BlockManager,
    PayloadManager,
    TransactionManager,
    AddressManager,
)
from .utils import get_merkle_root, pubkey_base64_to_rsa
from .helpers import CryptoTools

logger = logging.getLogger('django_info')


@python_2_unicode_compatible
class Block(models.Model):
    ''' Our Model for Blocks '''
    # Id block
    hash_block = models.CharField(max_length=255, blank=True, default="")
    previous_hash = models.CharField(max_length=255, blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    data = JSONField(default={}, blank=True)
    merkleroot = models.CharField(max_length=255, default="")
    poetxid = models.CharField(max_length=255, default="", blank=True)
    nonce = models.CharField(max_length=50, default="", blank=True)
    hashcash = models.CharField(max_length=255, default="", blank=True)

    objects = BlockManager()

    @cached_property
    def raw_size(self):
        # get the size of the raw html
        # TODO need improve
        size = (len(self.previous_hash)+len(self.hash_block)+ len(self.get_formatted_date())) * 8
        return size

    def get_block_data(self, tx_queryset):
        # Get the sum of hashes of last transaction in block size
        sum_hashes = ""
        try:
            hashes = []
            for tx in tx_queryset:
                sum_hashes += tx.txid
                hashes.append(tx.txid)
                tx.block = self
                tx.save()

            self.data["hashes"] = hashes
            merkleroot = get_merkle_root(tx_queryset)
            return {"sum_hashes": sum_hashes, "merkleroot": merkleroot}

        except Exception as e:
            logger.error("[BLOCK ERROR] get block data error : %s" % e)
            return ""


    def get_formatted_date(self, format_time='d/m/Y'):
        # Correct date and format
        localised_date = self.timestamp
        if not settings.DEBUG:
            localised_date = localised_date - timedelta(hours=6)
        return DateFormat(localised_date).format(format_time)

    def __str__(self):
        return self.hash_block


@python_2_unicode_compatible
class Transaction(models.Model):
    ''' Tx Model '''
    # Cryptographically enabled fields
    # Necessary infomation
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    raw_msg = models.TextField(blank=True, default="") # Anything can be stored here
    # block information
    block = models.ForeignKey('blockchain.Block', related_name='transactions', null=True, blank=True)
    signature = models.TextField(blank=True, default="")
    is_valid = models.BooleanField(default=False, blank=True)
    txid = models.TextField(blank=True, default="")
    previous_hash = models.TextField(blank=True, default="")
    # Details
    details = JSONField(default={}, blank=True)

    objects = TransactionManager()


    # Hashes msg_html with utf-8 encoding, saves this in and hash in _signature
    def hash(self):
        hash_object = hashlib.sha256(self.raw_msg)
        self.txid = hash_object.hexdigest()

    def create_raw_msg(self):
        # Create raw html and encode
        msg = (
            self.timestamp.isoformat() +
            self.signature +
            str(self.is_valid) +
            self.previous_hash
        )
        self.raw_msg = msg.encode('utf-8')

    @cached_property
    def get_previous_hash(self):
        ''' Get before hash transaction '''
        return self.previous_hash

    def __str__(self):
        return self.txid


@python_2_unicode_compatible
class Payload(Timestampable, IOBlockchainize, models.Model):
    ''' Simplified Rx Model '''

    # Owner track
    public_key = models.TextField("An Hex representation of Public Key Object", blank=True, default=True)

    # For TxTransfer
    transaction = models.ForeignKey('blockchain.Transaction', related_name='payloads', null=True, blank=True)

    objects = PayloadManager()


    def __str__(self):
        return self.hash_id

    # There are here Personalized methods for Blockchinize model
    @cached_property
    def get_formatted_date(self, format_time='d/m/Y'):
        # Correct date and format
        localised_date = self.timestamp
        if not settings.DEBUG:
            localised_date = localised_date - timedelta(hours=6)

        return DateFormat(localised_date).format(format_time)

    @cached_property
    def get_delta_datetime(self):
        ''' Fix 6 hours timedelta on rx '''
        return self.timestamp - timedelta(hours=6)

    @cached_property
    def get_before_hash(self):
        ''' Get before hash Payload '''
        return self.previous_hash



class Address(Timestampable, models.Model):
    ''' Table of addresses '''

    public_key_b64 = models.TextField("Public Key", default="", help_text='Format: Base 64', unique=True)
    address =  models.CharField("Address to get transactions", max_length=255, default="", help_text='Format: Base 58 and valid bitcoin address')
    is_valid = models.BooleanField("Check if address is valid", blank=True, default=True)

    objects = AddressManager()

    class Meta:
        ''' Custom Admin metadata'''
        verbose_name_plural = "Valid Bitcoin Addresses"
        ordering = ['created_at']

    def __str__(self):
        return self.address

    @property
    def get_pub_key(self):
        ''' GET Pub Key in PEM format '''
        pub_key , raw_public_key = pubkey_base64_to_rsa(self.public_key_b64)
        return raw_public_key
