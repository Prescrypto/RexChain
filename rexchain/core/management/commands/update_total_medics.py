from django.core.management.base import BaseCommand
from core.helpers import safe_set_cache
from blockchain.models import Payload


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ''' Update total medics on plataform
        The reason is that the queryset takes long time,
        better handle it with a cron than a realtime webserver request!
        '''
        total = Payload.objects.values("public_key").distinct("public_key").count()
        safe_set_cache("total_medics", total)
        self.stdout.write('[CRON JOB SUCCESS] Update total medics: {}'.format(total))
