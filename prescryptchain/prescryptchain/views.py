# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from blockchain.models import Prescription, Block


def home(request):
    LIMIT_SEARCH = 10
    rxs = Prescription.objects.all().order_by('-id')[:LIMIT_SEARCH]
    blocks = Block.objects.all().order_by('-id')[:LIMIT_SEARCH]
    return render(request, "home.html", {"prescriptions" : rxs, "rx_blocks": blocks })


def block_detail(request, block_hash):
    return render(request, "blockchain/block_detail.html", {})

def rx_detail(request, rx_hash):
    return render(request, "blockchain/rx_detail.html", {})