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
from .managers import BlockManager, MedicationManager, PrescriptionManager, TransactionManager
from .utils import get_merkle_root
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
        size = (len(self.get_before_hash)+len(self.hash_block)+ len(self.get_formatted_date())) * 8
        return size

    def get_block_data(self, rx_queryset):
        # Get the sum of hashes of last prescriptions in block size
        sum_hashes = ""
        try:
            self.data["hashes"] = []
            for rx in rx_queryset:
                sum_hashes += rx.rxid
                self.data["hashes"].append(rx.rxid)
                rx.block = self
                rx.save()
            merkleroot = get_merkle_root(rx_queryset)
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

    @cached_property
    def get_before_hash(self):
        ''' Get before hash block '''
        return self.previous_hash

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


# Simplified Rx Model
@python_2_unicode_compatible
class Prescription(models.Model):
    # Cryptographically enabled fields
    public_key = models.TextField(blank=True, default="")
    private_key = models.TextField(blank=True, default="") # Aquí puedes guardar el PrivateKey para desencriptar
    ### Patient and Medic data (encrypted)
    medic_name = models.TextField(blank=True, default="")
    medic_cedula = models.TextField(blank=True, default="")
    medic_hospital = models.TextField(blank=True, default="")
    patient_name = models.TextField(blank=True, default="")
    patient_age = models.TextField(blank=True, default="")
    diagnosis = models.TextField(default="")
    ### Public fields (not encrypted)
    # Misc
    # TODO ADD created_at time of server!
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    location = models.TextField(blank=True, default="")
    raw_msg = models.TextField(blank=True, default="") # Anything can be stored here
    location_lat = models.FloatField(null=True, blank=True, default=0) # For coordinates
    location_lon = models.FloatField(null=True, blank=True, default=0)
    # Rx Specific
    details = models.TextField(blank=True, default="")
    extras = models.TextField(blank=True, default="")
    bought = models.BooleanField(default=False)
    # Main
    block = models.ForeignKey('blockchain.Block', related_name='block', null=True, blank=True)
    signature = models.TextField(null=True, blank=True, default="")
    is_valid = models.BooleanField(default=True, blank=True)
    rxid = models.TextField(blank=True, default="")
    previous_hash = models.TextField(default="")

    objects = PrescriptionManager()

    # Hashes msg_html with utf-8 encoding, saves this in and hash in _signature
    def hash(self):
        hash_object = hashlib.sha256(self.raw_msg)
        self.rxid = hash_object.hexdigest()

    @cached_property
    def get_data_base64(self):
        # Return data of prescription on base64
        return {
            "medic_name" : self.medic_name,
            "medic_cedula" : self.medic_cedula,
            "medic_hospital" : self.medic_hospital,
            "patient_name" : self.patient_name,
            "patient_age" : self.patient_age,
            "diagnosis" : self.diagnosis
        }

    @property
    def get_priv_key(self):
        ''' Get private key on Pem string '''
        # Symbolic pass
        # Removing legacy code
        return ""


    @property
    def get_pub_key(self):
        ''' Get public key on Pem string '''
        # Symbolic pass
        # Removing legacy code
        return ""

    def create_raw_msg(self):
        # Create raw html and encode
        msg = (
            self.medic_name +
            self.medic_cedula +
            self.medic_hospital +
            self.patient_name +
            self.patient_age +
            self.diagnosis
        )
        self.raw_msg = msg.encode('utf-8')


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
    def raw_size(self):
        # get the size of the raw rx
        size = (
            len(self.raw_msg) + len(self.diagnosis) +
            len(self.location) + len(self.rxid) +
            len(self.medic_name) + len(self.medic_cedula) +
            len(self.medic_hospital) + len(self.patient_name) +
            len(self.patient_age) + len(str(self.get_formatted_date()))
        )
        if self.medications.all() is not None:
            for med in self.medications.all():
                size += len(med.presentation) +len(med.instructions)
        return size * 8

    @cached_property
    def get_before_hash(self):
        ''' Get before hash prescription '''
        return self.previous_hash


    def __str__(self):
        return self.rxid



@python_2_unicode_compatible
class Medication(models.Model):
    prescription = models.ForeignKey('blockchain.Prescription',
        related_name='medications'
        )
    active = models.TextField(blank=True, default="")
    presentation = models.TextField(blank=True, default="")
    instructions = models.TextField(blank=True, default="")
    frequency = models.TextField(blank=True, default="")
    dose = models.TextField(blank=True, default="")
    bought = models.BooleanField(default=False)
    drug_upc = models.TextField(blank=True, default="", db_index=True)

    objects = MedicationManager()

    def __str__(self):
        return self.presentation
