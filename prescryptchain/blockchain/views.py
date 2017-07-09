# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import View, CreateView, ListView
from django.shortcuts import render
from blockchain.forms import NewPrescriptionForm
from django.http import HttpResponseRedirect
import hashlib

# Create your views here.
# Create new prescription view, this is the biz

class AddPrescriptionView(View):
    template = 'blockchain/blockchain/new_rx.html'

    def get(self, request, *args, **kwargs):
        template = 'blockchain/new_rx.html'
        form = NewPrescriptionForm
        return render(request, template ,{"form": form,})

    def post(self, request, *args, **kwargs):
        template = 'blockchain/new_rx.html'
        form = NewPrescriptionForm(request.POST)
        if form.is_valid():
            rx = form.save(commit = False)
            rx.save()
            hash_object = hashlib.sha256(str(rx.timestamp))
            rx.signature = hash_object.hexdigest()
            rx.save()

        return HttpResponseRedirect('/')
