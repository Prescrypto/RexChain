""" Total payloads """
from django.core.management.base import BaseCommand
from core.helpers import safe_set_cache
from blockchain.models import Payload


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ''' Update total payloads on the platform
            The reason is that the queryset takes a long time,
            better handle it with a cron than a real-time web server request!
        '''
        total = Payload.objects.only("id").all().count()
        safe_set_cache("total_payloads", total)
        self.stdout.write('[CRON JOB SUCCESS] Update total payloads: {}'.format(total))
