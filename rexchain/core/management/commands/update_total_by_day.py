""" Total payloads """
from django.utils import timezone
from django.core.management.base import BaseCommand

from core.helpers import safe_set_cache
from blockchain.models import Payload


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ''' Update total payloads on the platform
            The reason is that the queryset takes a long time,
            better handle it with a cron than a real-time web server request!
        '''
        now = timezone.now()
        today_total =  self.filter(timestamp__date=now.date())
        safe_set_cache("rx_by_today", today_total)
        self.stdout.write('[CRON JOB SUCCESS] Update total payloads by today: {}'.format(today_total))
