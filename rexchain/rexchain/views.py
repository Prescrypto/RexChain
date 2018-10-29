# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from blockchain.models import Payload, Block


def home(request):
    ''' Home view'''
    logger = logging.getLogger('django_info')
    LIMIT_SEARCH = 10
    LIMIT_BLOCK = 5
    LAST_HOURS = 10
    _now = timezone.now()
    try:
        # Creating context for home view!
        context = {

            # Render
            "payloads" : Payload.objects.all().order_by('-id')[:LIMIT_SEARCH],
            "rx_blocks": Block.objects.all().order_by('-id')[:LIMIT_BLOCK],

            # Stats
            "payloads_total" : Payload.objects.all().count(),
            "total_medics": Payload.objects.total_medics(),
            "rx_by_today": Payload.objects.rx_by_today(_now).count(),

            # Deactivated
            # "rx_by_month": Payload.objects.rx_by_month(_now).count(),
            # "stats": json.dumps(Payload.objects.get_stats_last_hours(hours=LAST_HOURS)),
        }
        return render(request, "home.html", context)
    except Exception as e:
        logger.error("[View home ERROR]: {} Type: {}".format(e, type(e)))
        return HttpResponse(status=500)

def block_detail(request, block_hash):
    return render(request, "blockchain/block_detail.html", {})

def rx_detail(request, rx_hash):
    return render(request, "blockchain/rx_detail.html", {})

def humans_txt(request):
    ''' Show humans txt file '''
    response = render(request, 'humans.txt', {})
    response['Content-Type'] = "text/plain"
    return response

def robots_txt(request):
    ''' Show humans txt file '''
    response = render(request, 'robots.txt', {})
    response['Content-Type'] = "text/plain"
    return response
