# -*- encoding: utf-8 -*-
'''
Model Managers RexChain
BlockManager
RXmanager
TXmanager
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
from .helpers import genesis_hash_generator, GENESIS_INIT_DATA, get_genesis_merkle_root, CryptoTools
from .utils import calculate_hash, PoE, pubkey_base64_to_rsa, ordered_data, iterate_and_order_json
from .querysets import (
    PayloadQueryset,
    TransactionQueryset,
    AddressQueryset,
)
from .RSAaddresses import AddressBitcoin

logger = logging.getLogger('django_info')


class BlockManager(models.Manager):
    ''' Model Manager for Blocks '''

    def create_block(self, tx_queryset):
        # Do initial block or create next block
        Block = apps.get_model('blockchain', 'Block')
        last_block = Block.objects.last()
        if last_block is None:
            genesis = self.get_genesis_block()
            return self.generate_next_block(genesis.hash_block, tx_queryset)

        else:
            return self.generate_next_block(last_block.hash_block, tx_queryset)

    def get_genesis_block(self):
        # Get the genesis arbitrary block of the blockchain only once in life
        Block = apps.get_model('blockchain', 'Block')
        genesis_block = Block.objects.create(
            hash_block=genesis_hash_generator(),
            data=GENESIS_INIT_DATA,
            merkleroot=get_genesis_merkle_root())
        genesis_block.previous_hash = "0"
        genesis_block.save()
        return genesis_block

    def generate_next_block(self, hash_before, tx_queryset):
        # Generete a new block
        new_block = self.create(previous_hash=hash_before)
        new_block.save()
        data_block = new_block.get_block_data(tx_queryset)
        new_block.hash_block = calculate_hash(new_block.id, hash_before,
                                              str(new_block.timestamp), data_block["sum_hashes"])
        # Add Merkle Root
        new_block.merkleroot = data_block["merkleroot"]
        # Proof of Existennce layer
        _poe = PoE()  # init proof of existence element
        txid = _poe.journal(new_block.merkleroot)
        if txid is True:
            new_block.poetxid = "True"
        else:
            new_block.poetxid = "False"
        # Save
        new_block.save()

        return new_block


class TransactionManager(models.Manager):
    ''' Manager for Payloads '''

    _crypto = CryptoTools(has_legacy_keys=False)

    def get_queryset(self):
        return TransactionQueryset(self.model, using=self._db)

    def has_not_block(self):
        return self.get_queryset().has_not_block()

    def create_block_attempt(self):
        '''
            Use PoW hashcash algoritm to attempt to create a block
        '''
        Block = apps.get_model('blockchain', 'Block')
        _hashcash_tools = Hashcash(debug=settings.DEBUG)

        if not cache.get('challenge') and not cache.get('counter') == 0:
            challenge = _hashcash_tools.create_challenge(word_initial=settings.HC_WORD_INITIAL)
            safe_set_cache('challenge', challenge)
            safe_set_cache('counter', 0)

        is_valid_hashcash, hashcash_string = _hashcash_tools.calculate_sha(cache.get('challenge'),
                                                                           cache.get('counter'))

        if is_valid_hashcash:
            block = Block.objects.create_block(self.has_not_block())  # TODO add on creation hash and merkle
            block.hashcash = hashcash_string
            block.nonce = cache.get('counter')
            block.save()
            safe_set_cache('challenge', None)
            safe_set_cache('counter', None)

        else:
            counter = cache.get('counter') + 1
            safe_set_cache('counter', counter)

    def is_transfer_valid(self, data, _previous_hash, pub_key, _signature):
        ''' Method to handle transfer validity!'''
        Payload = apps.get_model('blockchain', 'Payload')
        if not Payload.objects.check_existence(data['previous_hash']):
            logger.info("[IS_TRANSFER_VALID] Send a transfer with a wrong reference previous_hash!")
            return (False, None)

        before_rx = Payload.objects.get(hash_id=data['previous_hash'])

        if not before_rx.readable:
            logger.info("[IS_TRANSFER_VALID]The before_rx is not readable")
            return (False, before_rx)

        # TODO ordered data
        try:
            json.dumps(data, separators=(',', ':'))
        except Exception as e:
            logger.error("[ERROR in reading data] {}, Type {}".format(e, type(e)))
            # _msg = ""
        # TODO add verify files data too

        # if not self._crypto.verify(_msg, _signature, self._crypto.un_savify_key(before_rx.public_key)):
        #     logger.info("[IS_TRANSFER_VALID]Signature is not valid!")
        #     return (False, before_rx)

        logger.info("[IS_TRANSFER_VALID] Success")
        return (True, before_rx)

    def create_tx(self, data, **kwargs):
        ''' Custom method for create Tx with rx item '''

        ''' Get initial data '''

        _payload = ""
        _signature = data.pop("signature", None)
        _previous_hash = data.pop("previous_hash", "0")
        # Get Public Key from API None per default
        data = data["data"]
        raw_pub_key = data.get("public_key", None)
        if not raw_pub_key:
            logger.error("[get public key ERROR]: Couldn't find public key outside data")

        ''' When timestamp is convert to python datetime needs this patch '''
        # timestamp = data["timestamp"]
        # timestamp.replace(tzinfo=timezone.utc)
        # data["timestamp"] = timestamp.isoformat()

        # Initalize some data
        try:
            # First we order the sub lists and sub jsons
            data = iterate_and_order_json(data)
            # Then we order the json
            data_sorted = ordered_data(data)
            _payload = json.dumps(data_sorted, separators=(',', ':'))

        except Exception as e:
            logger.error("[create_tx1 ERROR]: {}, type:{}".format(e, type(e)))

        _is_valid_tx = False
        _rx_before = None

        try:
            # Prescript unsavify method
            pub_key = self._crypto.un_savify_key(raw_pub_key)
        except Exception as e:
            logger.error("[Key is b64 WARNING]: {}, type:{}".format(e, type(e)))
            # Attempt to create public key with base64 with js payload
            pub_key, raw_pub_key = pubkey_base64_to_rsa(raw_pub_key)

        hex_raw_pub_key = self._crypto.savify_key(pub_key)
        ''' Get previous hash '''
        # _previous_hash = data.get('previous_hash', '0')
        logger.info("previous_hash: {}".format(_previous_hash))

        ''' Check initial or transfer '''
        if _previous_hash == '0':
            # It's a initial transaction
            if self._crypto.verify(_payload, _signature, pub_key):
                logger.info("[CREATE_TX] Tx valid!")
                _is_valid_tx = True

        else:
            # Its a transfer, so check validite transaction
            data["previous_hash"] = _previous_hash
            _is_valid_tx, _rx_before = self.is_transfer_valid(data, _previous_hash, pub_key, _signature)

        ''' FIRST Create the Transaction '''
        tx = self.create_raw_tx(data, _is_valid_tx=_is_valid_tx, _signature=_signature, pub_key=pub_key)

        ''' THEN Create the Data Item(Payload) '''
        Payload = apps.get_model('blockchain', 'Payload')
        rx = Payload.objects.create_rx(
            data,
            _signature=_signature,
            pub_key=hex_raw_pub_key,  # This is basically the address
            _is_valid_tx=_is_valid_tx,
            _rx_before=_rx_before,
            transaction=tx,
        )
        ''' LAST do create block attempt '''
        self.create_block_attempt()

        # Return the rx for transaction object
        return rx

    def create_raw_tx(self, data, **kwargs):
        ''' This method just create the transaction instance '''

        ''' START TX creation '''
        Transaction = apps.get_model('blockchain', 'Transaction')
        tx = Transaction()
        # Get Public Key from API
        tx.signature = kwargs.get("_signature", None)
        tx.is_valid = kwargs.get("_is_valid_tx", False)
        tx.timestamp = timezone.now()

        # Set previous hash
        if self.last() is None:
            tx.previous_hash = "0"
        else:
            tx.previous_hash = self.last().txid

        # Create raw data to generate hash and save it
        tx.create_raw_msg()
        tx.hash()
        tx.save()

        ''' RETURN TX '''
        return tx


class PayloadManager(models.Manager):
    ''' Manager for Payload Model '''

    def get_queryset(self):
        return PayloadQueryset(self.model, using=self._db)

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
        ''' Return a list of last rx created by given last hours '''
        RANGE_HOUR = 1
        _list = []
        _time = timezone.now()
        _list.append([get_timestamp(_time), self.range_by_hour(_time).count()])
        for i in range(0, hours):
            _time = _time - timedelta(hours=RANGE_HOUR)
            _list.append([get_timestamp(_time), self.range_by_hour(_time).count()])

        return _list

    def check_existence(self, previous_hash):
        return self.get_queryset().check_existence(previous_hash)

    def create_rx(self, data, **kwargs):
        rx = self.create_raw_rx(data, **kwargs)
        return rx

    def create_raw_rx(self, data, **kwargs):
        # This calls the super method saving all clean data first
        Payload = apps.get_model('blockchain', 'Payload')

        _rx_before = kwargs.get('_rx_before', None)

        rx = Payload(
            data=data,
            timestamp=data.get("timestamp", timezone.now()),
            public_key=kwargs.get("pub_key", ""),
            signature=kwargs.get("_signature", ""),
            is_valid=kwargs.get("_is_valid_tx", False),
            transaction=kwargs.get("transaction", None)
        )

        if "files" in data:
            rx.files = data["files"]

        if "location" in data:
            rx.location = data["location"]

        # Save previous hash
        if _rx_before is None:
            logger.info("[CREATE_RX] New transaction!")
            rx.previous_hash = "0"
            rx.readable = True
        else:
            logger.info("[CREATE_RX] New transaction transfer!")
            rx.previous_hash = _rx_before.hash_id
            if rx.is_valid:
                logger.info("[CREATE_RX] Tx transfer is valid!")
                rx.readable = True
                _rx_before.transfer_ownership()
            else:
                logger.info("[CREATE_RX] Tx transfer not valid!")

        rx.create_raw_msg()
        rx.hash()
        rx.save()

        return rx


class AddressManager(models.Manager):
    ''' Add custom Manager '''

    def get_queryset(self):
        return AddressQueryset(self.model, using=self._db)

    def check_existence(self, public_key_b64):
        return self.get_queryset().check_existence(public_key_b64)

    def get_rsa_address(self, public_key_b64):
        return self.get_queryset().get_rsa_address(public_key_b64)

    def create_rsa_address(self, public_key_b64):
        ''' Method to create new rsa address '''

        _addresses_generator = AddressBitcoin()
        _new_raw_address = _addresses_generator.create_address_bitcoin(public_key_b64)

        rsa_address = self.create(
            public_key_b64=public_key_b64,
            address=_new_raw_address,
        )
        rsa_address.save()
        return rsa_address.address

    def get_or_create_rsa_address(self, public_key_b64):
        ''' 'Check existence of address for public key '''
        if self.check_existence(public_key_b64):
            ''' Return correct address '''
            return self.get_rsa_address(public_key_b64)
        else:
            ''' Return a new address for the public key '''
            return self.create_rsa_address(public_key_b64)
