# -*- encoding: utf-8 -*-
# Python Libs
## Hash lib
import hashlib
import base64
from datetime import timedelta, datetime
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
from .utils import (
    un_savify_key, savify_key,
    encrypt_with_public_key, decrypt_with_private_key,
    calculate_hash, bin2hex, hex2bin,  get_new_asym_keys
)

# Setting block size
BLOCK_SIZE = settings.BLOCK_SIZE


class BlockManager(models.Manager):
    ''' Model Manager for Blocks '''
    def create_block(self):
        # Do initial block or create next block
        last_block = Block.objects.last()
        if last_block is None:
            genesis = self.get_genesis_block()
            return self.generate_next_block(hash_before=genesis.hash_block)

        else:
            return self.generate_next_block(hash_before=last_block.hash_block)

    def get_genesis_block(self):
        # Get the genesis arbitrary block of the blockchain only once in life
        genesis_block = Block.objects.create(hash_block="816534932c2b7154836da6afc367695e6337db8a921823784c14378abed4f7d7");
        genesis_block.save()
        return genesis_block

    def generate_next_block(self, hash_before):
        # Generete a new block

        new_block = self.create()
        new_block.save()

        new_block.hash_block = calculate_hash(new_block.id, hash_before, str(new_block.timestamp), new_block.get_block_data())
        new_block.save()

        return new_block


@python_2_unicode_compatible
class Block(models.Model):
    ''' Our Model for Blocks '''
    # Id block
    hash_block = models.CharField(max_length=255, blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    data = JSONField(default={}, blank=True)
    merkleroot = models.CharField(max_length=255, default="")
    objects = BlockManager()

    @cached_property
    def raw_size(self):
        # get the size of the raw html
        size = (len(self.get_before_hash)+len(self.hash_block)+ len(self.get_formatted_date())) * 8
        return size

    def get_block_data(self):
        # Get the sum of hashes of last prescriptions in block size
        sum_hashes = ""
        try:
            prescriptions = Prescription.objects.all().order_by('-timestamp')[:BLOCK_SIZE]
            self.data["hashes"] = []
            for rx in prescriptions:
                sum_hashes += rx.signature
                self.data["hashes"].append(rx.signature)

            return sum_hashes

        except Exception as e:
            print("Error was found: %s" % e)
            return ""


    def get_formatted_date(self, format_time='d/m/Y'):
        # Correct date and format
        localised_date = self.timestamp
        if not settings.DEBUG:
            localised_date = localised_date - timedelta(hours=6)
        return DateFormat(localised_date).format(format_time)

    @cached_property
    def get_before_hash(self, count=1):
        ''' Get before hash block '''
        if self.id == 1:
            # number one block
            return "0"
        elif self.id > 1:
            # look for hash before
            try:
                block_before = Block.objects.get(id=(self.id - count))
                return block_before.hash_block

            except Exception as e:
                self.get_before_hash(count = count + 1)

    def __str__(self):
        return self.hash_block


# Simplified Rx Model
@python_2_unicode_compatible
class Prescription(models.Model):
    # Cryptographically enabled fields
    public_key = models.CharField(max_length=2000, blank=True, default="")
    private_key = models.CharField(max_length=2000, blank=True, default="") # Aquí puedes guardar el PrivateKey para desencriptar
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
    location_lat = models.FloatField(null=True, blank=True, default=0) # For coordinates
    location_lon = models.FloatField(null=True, blank=True, default=0)
    # Rx Specific
    details = models.TextField(blank=True, max_length=10000, default="")
    extras = models.TextField(blank=True, max_length=10000, default="")
    bought = models.BooleanField(default=False)
    # Main
    signature = models.CharField(max_length=255, blank=True, default="")

    # Hashes msg_html with utf-8 encoding, saves this in raw_html_msg and hash in signature
    def sign(self):
        hash_object = hashlib.sha256(self.raw_msg)
        self.signature = hash_object.hexdigest()

    @cached_property
    def get_data_base64(self):
        # Return data of prescription on base64
        return {
            "medic_name" : base64.b64encode(hex2bin(self.medic_name)),
            "medic_cedula" : base64.b64encode(hex2bin(self.medic_cedula)),
            "medic_hospital" : base64.b64encode(hex2bin(self.medic_hospital)),
            "patient_name" : base64.b64encode(hex2bin(self.patient_name)),
            "patient_age" : base64.b64encode(hex2bin(self.patient_age)),
            "diagnosis" : base64.b64encode(hex2bin(self.diagnosis))
        }

    @cached_property
    def get_priv_key(self):
        key = un_savify_key(self.private_key)
        return key.save_pkcs1(format="PEM")

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


    def save(self, *args, **kwargs):
        # This call the super method save saving all clean data first
        new_rx = False
        if self.pk is None:
            new_rx = True
            (pub_key, priv_key) = get_new_asym_keys()
            self.public_key = savify_key(pub_key)
            self.private_key = savify_key(priv_key)
            self.medic_name = bin2hex(encrypt_with_public_key(self.medic_name.encode("utf-8"), pub_key))
            self.medic_cedula = bin2hex(encrypt_with_public_key(self.medic_cedula.encode("utf-8"), pub_key))
            self.medic_hospital = bin2hex(encrypt_with_public_key(self.medic_hospital.encode("utf-8"), pub_key))
            self.patient_name = bin2hex(encrypt_with_public_key(self.patient_name.encode("utf-8"), pub_key))
            self.patient_age = bin2hex(encrypt_with_public_key(str(self.patient_age).encode("utf-8"), pub_key))
            self.diagnosis = bin2hex(encrypt_with_public_key(self.diagnosis.encode("utf-8"), pub_key))
            self.create_raw_msg()
            self.sign()

        super(Prescription, self).save(*args, **kwargs)
        # THIS is where we create the next BLOCK
        if new_rx:
            # Post save check if the rx made a new block
            if self.id % BLOCK_SIZE == 0:
                # Here is where create the block
                Block.objects.create_block()



    def get_formatted_date(self, format_time='d/m/Y'):
        # Correct date and format
        localised_date = self.timestamp
        if not settings.DEBUG:
            localised_date = localised_date - timedelta(hours=6)

        return DateFormat(localised_date).format(format_time)

    @cached_property
    def raw_size(self):
        # get the size of the raw rx
        size = (
            len(self.raw_msg) + len(self.diagnosis) +
            len(self.location) + len(self.signature) +
            len(self.medic_name) + len(self.medic_cedula) +
            len(self.medic_hospital) + len(self.patient_name) +
            len(self.patient_age) + len(str(self.get_formatted_date()))
        )
        return size * 8

    @cached_property
    def get_before_hash(self, count=1):
        ''' Get before hash prescription '''
        if self.id == 1:
            # number one prescription
            return self.signature
        try:
            rx_before = Prescription.objects.get(id=(self.id - count))
            return rx_before.signature

        except Exception as e:
            self.get_before_hash(count = count + 1)


    def __str__(self):
        # podriamos reducirlo a solo nombre y poner los demas campos en el admin django! CHECAR  ESTO
        return self.medic_name

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
        return self.drug_upc
