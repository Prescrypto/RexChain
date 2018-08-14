# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.shortcuts import render
from django.http import HttpResponse

from blockchain.models import Prescription, Block


def home(request):
    ''' Home view'''
    logger = logging.getLogger('django_info')
    LIMIT_SEARCH = 10
    LIMIT_BLOCK = 5
    LAST_HOURS = 10
    try:
        # Creating context for home view!
        context = {
            "stats": Prescription.objects.get_stats_last_hours(hours=LAST_HOURS),
            "prescriptions" : Prescription.objects.all().order_by('-id')[:LIMIT_SEARCH],
            "rx_blocks": Block.objects.all().order_by('-id')[:LIMIT_BLOCK],
            "total_medics": Prescription.objects.total_medics().count(),
            "rx_by_today": Prescription.objects.rx_by_today().count(),
            "rx_by_month": Prescription.objects.rx_by_month().count(),
        }
        return render(request, "home.html", context)
    except Exception as e:
        logger.error("[View home ERROR]: {} Type: {}".format(e, type(e)))
        return HttpResponse(status=500)

def block_detail(request, block_hash):
    return render(request, "blockchain/block_detail.html", {})

def rx_detail(request, rx_hash):
    return render(request, "blockchain/rx_detail.html", {})

def humanstxt(request):
    ''' Show humans txt file '''
    response = render(request, 'humans.txt', {})
    response['Content-Type'] = "text/plain"
    return response

