# -*- encoding: utf-8 -*-
# Python Libs
## Hash lib
import hashlib
from datetime import timedelta, datetime
# Unicode shite
import unicodedata
# Django Libs
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.dateformat import DateFormat
# Our methods
from .utils import (
    un_savify_key, un_savify_key,
    encrypt_with_public_key, decrypt_with_private_key,
    calculate_hash
)


class BlockManager(models.Manager):
    ''' Model Manager for Blocks '''
    def create_block(self, id,  previousHash, timestamp, data, block_hash):
        if previousHash == "0":
            new_block = self.get_genesis_block()
            return new_block
        else:
            new_block = Block.create(hash_anterior=previousHash, timestamp=timestamp, hash_block=block_hash)
            return new_block

    def get_genesis_block(self):
        # Get the genesis arbitrary block of the blockchain only once in life
        genesis_block = Block.create(0, "0", 1465154705, "My genesis block!!", "816534932c2b7154836da6afc367695e6337db8a921823784c14378abed4f7d7");
        genesis_block.save()
        return genesis_block

    def generate_next_block(self, block_data):
        # Generete a new block
        previous_block = self.queryset().last()
        next_index = previous_block.id + 1
        next_timestamp = datetime.date.now()
        next_hash = calculate_hash(next_index, previous_block.hash_block, next_timestamp, block_data)
        new_block = self.create(next_index, previous_block.hash_block, next_timestamp, block_data, nextHash)
        new_block.save()
        return new_block


@python_2_unicode_compatible
class Block(models.Model):
    hash_anterior = models.CharField(max_length=255, default="")
    hash_block = models.CharField(max_length=255, default="")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = BlockManager()

    @cached_property
    def raw_size(self):
        # get the size of the raw html
        size = len(self.hash_anterior)+len(self.hash_block)+len(self.get_formatted_date())  * 8
        return size

    def get_formatted_date(self, format_time='d/m/Y'):
        # Correct date and format
        localised_date = self.timestamp
        if not settings.DEBUG:
            localised_date = localised_date - timedelta(hours=6)
        return DateFormat(localised_date).format(format_time)

    def __str__(self):
        return hash_block


# class PrescriptionManager(models.ManagerModel):
#     ''' Prescription Model Manager for prescriptions '''
#     def create(self, public_key, private_key, data, *args, **kwargs):


# Simplified Rx Model
@python_2_unicode_compatible
class Prescription(models.Model):
    # Cryptographically enabled fields
    public_key = models.CharField(max_length=2000, default="")
    private_key = models.CharField(max_length=2000, default="") # Aquí puedes guardar el PrivateKey para desencriptar
    ### Patient and Medic data (encrypted)
    medic_name = models.CharField(blank=True, max_length=255, default="")
    medic_cedula = models.CharField(blank=True, max_length=255, default="")
    medic_hospital = models.CharField(blank=True, max_length=255, default="")
    patient_name = models.CharField(blank=True, max_length=255, default="")
    patient_age = models.CharField(blank=True, max_length=255, default="")
    diagnosis = models.CharField(max_length=255, default="")
    ### Public fields (not encrypted)
    # Misc
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    location = models.CharField(blank=True, max_length=255, default="")
    raw_msg = models.TextField(max_length=10000, blank=True, default="") # Anything can be stored here
    location_lat = models.FloatField(default=0) # For coordinates
    location_lon = models.FloatField(default=0)
    # Rx Specific
    details = models.TextField(blank=True, max_length=10000, default="")
    extras = models.TextField(blank=True, max_length=10000, default="")
    bought = models.BooleanField(default=False)
    # Main
    signature = models.CharField(max_length=255, default="")
    data = JSONField()

    # Hashes msg_html with utf-8 encoding, saves this in raw_html_msg and hash in signature
    def sign(self):
        hash_object = hashlib.sha256(self.raw_msg)
        self.signature = hash_object.hexdigest()
        self.save()

    def create_raw_msg(self):
        # Create raw html and encode
        msg = "" # Fix later
        self.raw_html_msg = msg.encode('utf-8')
        self.save()

    def save(self):
        self.medic_name = encrypt(self.medic_name, self.public_key)
        self.medic_cedula = encrypt(self.medic_cedula, self.public_key)
        self.medic_hospital = encrypt(self.medic_hospital, self.public_key)
        self.patient_name = encrypt(self.patient_name, self.public_key)
        self.patient_age = encrypt(self.patient_age, self.public_key)
        self.diagnosis = encrypt(self.diagnosis, self.public_key)
        self.save()
        # Este es el fix
        super(Prescription, self).save()

    def get_formatted_date(self, format_time='d/m/Y'):
        # Correct date and format
        localised_date = self.timestamp
        if not settings.DEBUG:
            localised_date = localised_date - timedelta(hours=6)

        return DateFormat(localised_date).format(format_time)

    @cached_property
    def raw_size(self):
        # get the size of the raw html
        size = (
            len(self.medic_public_key)+len(self.patient_public_key)+
            len(self.diagnosis)+len(self.location)+
            len(self.raw_msg)+len(self.location_lat)+
            len(self.location_lon)+len(self.details)+
            len(self.extras)+len(self.signature)+
            len(self.public_key)+int(self.bought)+
            len(self.get_formatted_date())  * 8
        )
        return size

    def __str__(self):
        # podriamos reducirlo a solo nombre y poner los demas campos en el admin django! CHECAR  ESTO
        return signature

@python_2_unicode_compatible
class Medication(models.Model):
    prescription = models.ForeignKey('blockchain.Prescription',
        related_name='medications'
        )
    active = models.CharField(blank=True, max_length=255, default="")
    presentation = models.CharField(
        blank=True, max_length=255,
    )
    instructions = models.TextField(blank=True, max_length=10000, default="")
    frequency = models.CharField(blank=True, max_length=255, default="")
    dose = models.CharField(blank=True, max_length=255, default="")
    bought = models.BooleanField(default=False)
    drug_upc = models.CharField(blank=True, max_length=255, default="", db_index=True)

    public_key = models.CharField(max_length=255, default="")

    def save(self):
        self.encrypt()
        super(Prescription, self).save()

    def encrypt():
        pass

    def __str__(self):
        return drug_upc
