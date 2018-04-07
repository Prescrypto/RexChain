# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.shortcuts import render

from blockchain.models import Prescription, Block


def home(request):
    ''' Home view'''
    logger = logging.getLogger('django_info')
    LIMIT_SEARCH = 10
    LIMIT_BLOCK = 5
    rxs = Prescription.objects.all().order_by('-id')[:LIMIT_SEARCH]
    blocks = Block.objects.all().order_by('-id')[:LIMIT_BLOCK]
    logger.info('Total Blocks: {}'.format(blocks.count()))
    return render(request, "home.html", {"prescriptions" : rxs, "rx_blocks": blocks })


def block_detail(request, block_hash):
    return render(request, "blockchain/block_detail.html", {})

def rx_detail(request, rx_hash):
    return render(request, "blockchain/rx_detail.html", {})

def humanstxt(request):
    ''' Show humans txt file '''
    response = render(request, 'humans.txt', {})
    response['Content-Type'] = "text/plain"
    return response

