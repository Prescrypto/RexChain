''' List of querysets '''
from django.db import models
from django.core.cache import cache


class PayloadQueryset(models.QuerySet):
    ''' Add custom querysets'''

    def check_existence(self, previous_hash):
        return self.filter(hash_id=previous_hash).exists()

    def non_validated_rxs(self):
        return self.filter(is_valid=True).filter(block=None)

    def total_medics(self):
        ''' Get total medics, performance search with cache '''
        return cache.get('total_medics', '90')

    def total_payloads(self):
        ''' Get total payloads, performance search with cache '''
        return cache.get('total_payloads', '528990')

    def rx_by_today(self):
        ''' Get total rx by today, with cache'''
        return cache.get('rx_by_today', '1618')


class TransactionQueryset(models.QuerySet):
    ''' Add custom querysets'''

    def has_not_block(self):
        return self.filter(block=None)


class AddressQueryset(models.QuerySet):
    ''' Add custom querysets'''

    def check_existence(self, public_key_b64):
        return self.filter(public_key_b64=public_key_b64).exists()

    def get_rsa_address(self, public_key_b64):
        _record = self.filter(public_key_b64=public_key_b64).first()
        return _record.address
