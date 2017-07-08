# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render


def home(request):
    return render(request, "home.html", {})


def block_detail(request, block_hash):
    return render(request, "blockchain/block_detail.html", {})

def rx_detail(request, rx_hash):
    return render(request, "blockchain/rx_detail.html", {})