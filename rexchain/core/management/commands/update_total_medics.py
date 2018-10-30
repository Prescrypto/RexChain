from django.core.management.base import BaseCommand
from django.core.cache import cache

from core.helpers import safe_set_cache
from blockchain.models import Payload

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ''' Update total medics on plataform
        The reason is the queryset takes long time, better handle with cron thant realtime webserver request!
        '''
        total = Payload.objects.values("public_key").distinct("public_key").count()
        safe_set_cache("total_medics", total)
        self.stdout.write('[CRON JOB SUCCESS] Update total medics: {}'.format(total))

