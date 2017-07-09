# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import View, CreateView, ListView
from django.shortcuts import render
from blockchain.forms import NewPrescriptionForm

# Create your views here.
# Create new prescription view, this is the biz

class AddPrescriptionView(View):
    template = 'new_rx.html'

    def get(self, request, *args, **kwargs):
        form = NewPrescriptionForm
        return render(request, template ,{"form": form,})

    def post(self, request, *args, **kwargs):
        form = NewPrescriptionForm(request.POST)
        if form.is_valid():
            print "yes"
        return render(request, template ,{"data": prescription_data})
