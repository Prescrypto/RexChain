# -*- encoding: utf-8 -*-
'''
Model Managers RxChain
BlockManager
RXmanager
TXmanager
MedicationManager
'''
import json
import logging
from datetime import timedelta

from django.db import models
from django.apps import apps
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from core.utils import Hashcash
from core.helpers import safe_set_cache, get_timestamp
from api.exceptions import EmptyMedication, FailedVerifiedSignature

from .helpers import genesis_hash_generator, GENESIS_INIT_DATA, get_genesis_merkle_root, CryptoTools
from .utils import calculate_hash, get_merkle_root, PoE
from .querysets import PrescriptionQueryset

logger = logging.getLogger('django_info')

class BlockManager(models.Manager):
    ''' Model Manager for Blocks '''

    def create_block(self, rx_queryset):
        # Do initial block or create next block
        last_block = Block.objects.last()
        if last_block is None:
            genesis = self.get_genesis_block()
            return self.generate_next_block(genesis.hash_block, rx_queryset)

        else:
            return self.generate_next_block(last_block.hash_block, rx_queryset)

    def get_genesis_block(self):
        # Get the genesis arbitrary block of the blockchain only once in life
        Block = apps.get_model('blockchain','Block')
        genesis_block = Block.objects.create(
            hash_block=genesis_hash_generator(),
            data=GENESIS_INIT_DATA,
            merkleroot=get_genesis_merkle_root())
        genesis_block.hash_before = "0"
        genesis_block.save()
        return genesis_block

    def generate_next_block(self, hash_before, rx_queryset):
        # Generete a new block

        new_block = self.create(previous_hash=hash_before)
        new_block.save()
        data_block = new_block.get_block_data(rx_queryset)
        new_block.hash_block = calculate_hash(new_block.id, hash_before, str(new_block.timestamp), data_block["sum_hashes"])
        # Add Merkle Root
        new_block.merkleroot = data_block["merkleroot"]
        # Proof of Existennce layer
        try:
            _poe = PoE() # init proof of existence element
            txid = _poe.journal(new_block.merkleroot)
            if txid is not None:
                new_block.poetxid = txid
            else:
                new_block.poetxid = ""
        except Exception as e:
            new_block.poetxid = ""
            logger.error("[PoE generate Block Error]: {}, type:{}".format(e, type(e)))

        # Save
        new_block.save()

        return new_block


class MedicationManager(models.Manager):
    ''' Manager to create Medication from API '''
    def create_medication(self, prescription, **kwargs):
        med = self.create(prescription=prescription, **kwargs)
        med.save()
        return med


class PrescriptionManager(models.Manager):
    ''' Manager for prescriptions '''

    def get_queryset(self):
        return PrescriptionQueryset(self.model, using=self._db)

    def range_by_hour(self, date_filter):
        return self.get_queryset().range_by_hour(date_filter)

    def non_validated_rxs(self):
        return self.get_queryset().non_validated_rxs()

    def total_medics(self):
        return self.get_queryset().total_medics()

    def rx_by_today(self, date_filter):
        return self.get_queryset().rx_by_today(date_filter)

    def rx_by_month(self, date_filter):
        return self.get_queryset().rx_by_month(date_filter)

    def get_stats_last_hours(self, hours=10):
        ''' Return a list of  last rx created by given last hours '''
        RANGE_HOUR = 1
        _list = []
        _new_time = _time = timezone.now()
        _list.append([get_timestamp(_time), self.range_by_hour(_time).count()])
        for i in range(0, hours):
            _time = _time - timedelta(hours=RANGE_HOUR)
            _list.append([get_timestamp(_time), self.range_by_hour(_time).count()])

        return _list

    def create_block_attempt(self):
        ''' Use PoW hashcash algoritm to attempt to create a block '''
        _hashcash_tools = Hashcash(debug=True)
        if not cache.get('challenge') and not cache.get('counter') == 0:
            challenge = _hashcash_tools.create_challenge(word_initial=settings.HC_WORD_INITIAL)
            safe_set_cache('challenge', challenge)
            safe_set_cache('counter', 0)

        is_valid_hashcash, hashcash_string = _hashcash_tools.calculate_sha(cache.get('challenge'), cache.get('counter'))

        if is_valid_hashcash:
            block = Block.objects.create_block(self.non_validated_rxs()) # TODO add on creation hash and merkle
            block.hashcash = hashcash_string
            block.nonce = cache.get('counter')
            block.save()
            safe_set_cache('challenge', None)
            safe_set_cache('counter', None)

        else:
            counter = cache.get('counter') + 1
            safe_set_cache('counter', counter)


    def create_rx(self, data, **kwargs):

        rx = self.create_raw_rx(data)

        if "medications" in data and len(data["medications"]) != 0:
            for med in data["medications"]:
                Medication.objects.create_medication(prescription=rx, **med)

        return rx

    def create_raw_rx(self, data, **kwargs):
        # This calls the super method saving all clean data first
        Prescription = apps.get_model('blockchain','Prescription')
        rx = Prescription()
        _crypto = CryptoTools()

        # Get Public Key from API, First try its with legacy crypto tools, then New Keys
        raw_pub_key = data.get("public_key")
        try:
            pub_key = _crypto.un_savify_key(raw_pub_key) # Make it usable
        except Exception as e:
            logger.info("[CREATE RAW RX, change to New Keys]")
            _crypto = CryptoTools(has_legacy_keys=False)
            pub_key = _crypto.un_savify_key(raw_pub_key)

        # Extract signature
        _signature = data.pop("signature", None)

        rx.medic_name = data["medic_name"]
        rx.medic_cedula = data["medic_cedula"]
        rx.medic_hospital = data["medic_hospital"]
        rx.patient_name = data["patient_name"]
        rx.patient_age = data["patient_age"]
        rx.diagnosis = data["diagnosis"]

        # This is basically the address
        rx.public_key = raw_pub_key

        if "location" in data:
            rx.location = data["location"]

        rx.timestamp = data["timestamp"]
        rx.create_raw_msg()

        rx.hash()
        # Save signature
        rx.signature = _signature

        #This block cath two cases when has_legacy_key is True or False
        if _crypto.verify(json.dumps(sorted(data)), _signature, pub_key):
            rx.is_valid = True
        else:
            rx.is_valid = False

        # Save previous hash
        if self.last() is None:
            rx.previous_hash = "0"
        else:
            rx.previous_hash = self.last().rxid

        rx.save()

        self.create_block_attempt()

        return rx

