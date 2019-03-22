# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# REST
import logging

from rest_framework.viewsets import ViewSetMixin
from rest_framework import routers, serializers, viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework import mixins, generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
# our models
from blockchain.models import Block, Payload, Transaction, Address
from blockchain.utils import pubkey_string_to_rsa, pubkey_base64_to_rsa, pubkey_base64_from_uri

from blockchain.helpers import CryptoTools

from .exceptions import NonValidPubKey

# Define router
router = routers.DefaultRouter()
logger = logging.getLogger('django_info')


class PayloadSerializer(serializers.ModelSerializer):
    """ Payload serializer """
    previous_hash = serializers.CharField(read_only=False, required=False, default="0")
    data = serializers.JSONField(binary=False, read_only=False, required=False)

    class Meta:
        model = Payload
        fields = (
            'data',
            'signature',
            'previous_hash',
            'hash_id',
            'is_valid',
            'transaction',
            'readable',
            'public_key',
        )
        read_only_fields = ('hash_id', 'previous_hash', 'is_valid', 'transaction', 'readable', 'public_key')

    def validate(self, data):
        ''' Method to control Extra Keys on Payload!'''
        extra_keys = set(self.initial_data.keys()) - set(self.fields.keys())
        if extra_keys:
            logger.info("Extra Keys: ", extra_keys)
        return data

    def create(self, validated_data):
        return Transaction.objects.create_tx(data=validated_data)


class PayloadViewSet(viewsets.ModelViewSet):
    """ Payload Viewset """
    # Temporally without auth
    # authentication_classes = (TokenAuthentication, BasicAuthentication, )
    # permission_classes = (IsAuthenticated, )
    serializer_class = PayloadSerializer
    lookup_field = "hash_id"
    http_method_names = ['get', 'post', 'options']

    def get_queryset(self):
        ''' Custom Get queryset '''
        raw_public_key = self.request.query_params.get('public_key', None)
        if raw_public_key:
            _crypto = CryptoTools(has_legacy_keys=False)

            pub_key, raw_public_key = pubkey_base64_to_rsa(raw_public_key)

            try:
                # pub_key = _crypto.get_pub_key_from_pem(raw_public_key)
                hex_raw_pub_key = _crypto.savify_key(pub_key)
            except Exception as e:
                logger.error("[Public Key Error]:{}, type:{}".format(e, type(e)))
                raise NonValidPubKey

            return Payload.objects.filter(public_key=hex_raw_pub_key).order_by('-id')
        else:
            return Payload.objects.all().order_by('-id')


# add patient filter by email, after could modify with other
# TODO change for new endpoint url
router.register(r'rx-endpoint', PayloadViewSet, 'payload-endpoint')


class BlockSerializer(serializers.ModelSerializer):
    """ Payload serializer """
    class Meta:
        model = Block
        fields = (
            'id',
            'hash_block',
            'previous_hash',
            'raw_size',
            'data',
            'timestamp',
            'merkleroot',
            'hashcash',
            'nonce',
            'public_key',
        )
        read_only_fields = ('id', 'hash_block','timestamp','previous_hash', 'raw_size', 'data', 'merkleroot',
                            'hashcash','nonce','public_key',)


class BlockViewSet(viewsets.ModelViewSet):
    """ Block Viewset """
    serializer_class = BlockSerializer

    def get_queryset(self):
        return Block.objects.all().order_by('-timestamp')


# add patient filter by email, after could modify with other
router.register(r'block', BlockViewSet, 'block-endpoint')


class AddressSerializer(serializers.ModelSerializer):
    """ Address serializer """
    pub_key = serializers.CharField(read_only=True, allow_null=True, source="get_pub_key")

    class Meta:
        model = Address
        fields = (
            'public_key_b64',
            'address',
            'is_valid',
            'pub_key',
        )
        read_only_fields = ('address', 'pub_key', )


class AddressViewSet(viewsets.ModelViewSet):
    """ Address Viewset """
    serializer_class = AddressSerializer
    lookup_field = "address"
    http_method_names = ['get', 'options']

    def get_queryset(self):
        ''' Custom Get queryset '''
        raw_public_key = self.request.query_params.get('public_key', None)
        if raw_public_key:
            try:
                pub_key_b64 = pubkey_base64_from_uri(raw_public_key)

            except Exception as e:
                raise NonValidPubKey
            else:
                _address = Address.objects.get_or_create_rsa_address(pub_key_b64)
                return Address.objects.filter(address=_address)

        else:
            return Address.objects.all()


# add patient filter by email, after could modify with other
router.register(r'address', AddressViewSet, 'address_endpoint')
