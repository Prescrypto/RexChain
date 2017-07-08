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
# AESCipher
from core.utils import AESCipher
# Create your models here.

from django.utils.functional import cached_property
from django.utils.dateformat import DateFormat



@python_2_unicode_compatible
class Block(models.Model):
    hash_anterior = models.CharField(max_length=255, default="")
    hash = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    @cached_property
    def raw_size(self):
        # get the size of the raw html
        size = len(self.hash_anterior)+len(self.hash)+len(self.get_formatted_date())  * 8
        return size

    # ======== Maybe this is useful????
    # # Hashes the request payload with utf-8 encoding
    # def sign(self, sum_payload):
    #     hash_object = hashlib.sha256(sum_payload)
    #     self.hash = hash_object.hexdigest()
    #     self.save()

    # def encrypt(self, signatures):
    #     # Encrypt the hash, using AES
    #     # Receives signatures array
    #     message = self.hash
    #     for sign in signatures:
    #         AEScipher = AESCipher(sign["hash"])
    #         message = AEScipher.encrypt(message)
    #     self.signature = message

    # def decrypt(self):
    #     # Returns the signature hash
    #     message = self.signature
    #     signatures = self.signatures.all()
    #     for sign in signatures[::-1]:
    #         AEScipher = AESCipher(sign.hash) # Accesing Signature property
    #         message = AEScipher.decrypt(message)
    #     return message
    def get_formatted_date(self, format_time='d/m/Y'):
        # Correct date and format
        localised_date = self.created_at
        if not settings.DEBUG:
            localised_date = localised_date - timedelta(hours=6)
        return DateFormat(localised_date).format(format_time)

    def __str__(self):
        return hash


# Simplified Rx Model
@python_2_unicode_compatible
class Prescription(models.Model):
    # Cryptographically enabled fields
    public_key = models.CharField(max_length=2000, default="")
    private_key = models.CharField(max_length=2000, default="")
    ### Patient and Medic data (encrypted)
    medic_name = models.CharField(blank=True, max_length=255, default="")
    medic_cedula = models.CharField(blank=True, max_length=255, default="")
    medic_hospital = models.CharField(blank=True, max_length=255, default="")
    patient_name = models.CharField(blank=True, max_length=255, default="")
    patient_age = models.CharField(blank=True, max_length=255, default="")
    diagnosis = models.CharField(max_length=255, default="")
    ### Public fields (not encrypted)
    # Misc
    timestamp = models.DateTimeField(default=datetime.now, db_index=True)
    location = models.CharField(blank=True, max_length=255, default="")
    raw_msg = models.TextField(max_length=10000, default="") # Anything can be stored here
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
        self.encrypt()
        super(Prescription, self).save()

    def encrypt():
        pass

    def get_formatted_date(self, format_time='d/m/Y'):
        # Correct date and format
        localised_date = self.timestamp
        if not settings.DEBUG:
            localised_date = localised_date - timedelta(hours=6)

        return DateFormat(localised_date).format(format_time)
    @cached_property
    def raw_size(self):
        # get the size of the raw html
        size = len(self.medic_public_key)+len(self.patient_public_key)+
        len(self.diagnosis)+len(self.location)+
        len(self.raw_msg)+len(self.location_lat)+
        len(self.location_lon)+len(self.details)+
        len(self.extras)+len(self.signature)+
        len(self.public_key)+int(self.bought)+
        len(self.get_formatted_date())  * 8
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
