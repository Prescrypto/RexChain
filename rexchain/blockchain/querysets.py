''' List of querysets '''
from django.db import models

class PrescriptionQueryset(models.QuerySet):
    ''' Add custom querysets'''

    def check_existence(self, previous_hash):
        return self.filter(hash_id=previous_hash).exists()

    def non_validated_rxs(self):
        return self.filter(is_valid=True).filter(block=None)

    def total_medics(self):
        return self.distinct("public_key")

    def rx_by_today(self, date_filter):
        return self.filter(timestamp__date=date_filter.date())

    def rx_by_month(self, date_filter):
        _date = date_filter.date()
        return self.filter(timestamp__year=_date.year).filter(timestamp__month=_date.month)

    def range_by_hour(self, date_filter):
        _date = date_filter.date()
        _time = date_filter.time()
        return self.filter(timestamp__year=_date.year).filter(timestamp__month=_date.month).filter(timestamp__day=_date.day).filter(timestamp__hour=_time.hour)


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
