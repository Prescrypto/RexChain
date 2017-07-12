# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python libs
import hashlib
# Django packages
from django.shortcuts import render, redirect
from django.views.generic import View, CreateView, ListView
# Our Models
from .forms import NewPrescriptionForm
from .models import Prescription



class AddPrescriptionView(View):
    ''' Simple Rx Form '''
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

        return redirect('/')


def rx_detail(request, hash_rx=False):
    ''' Get a hash and return the rx '''
    if request.GET.get("hash_rx", False):
        hash_rx = request.GET.get("hash_rx")

    if hash_rx:
        template = "blockchain/rx_detail.html"
        context = {}
        try:
            rx = Prescription.objects.get(signature=hash_rx)
            context["rx"] = rx
            try:
                hash_before = Prescription.objects.get(id=(rx.id -1))
                context["hash_before"] = hash_before.signature
            except Exception as e:
                print("Error found: %s, type: %s" % (e, type(e)))

            return render(request, template, context)
        except Exception as e:
            print("Error found: %s, type: %s" % (e, type(e)))

    return redirect("/")
