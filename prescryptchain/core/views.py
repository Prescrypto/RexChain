# -*- coding: utf-8 -*-
from django.utils import timezone
from django.http import JsonResponse
from django.views.generic import View

from blockchain.models import Prescription
from core.helpers import get_timestamp


class TxStatistics(View):
    ''' Endpoint to view TX Statics '''

    def get(self, request):
        ''' GET endpoint for Txs '''
        LAST_HOURS = 10
        data = Prescription.objects.get_stats_last_hours(hours=LAST_HOURS)
        return JsonResponse(data, safe=False)
