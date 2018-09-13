''' List of querysets '''
from django.db import models

class PrescriptionQueryset(models.QuerySet):
    ''' Add custom querysets'''

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
