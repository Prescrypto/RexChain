# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from blockchain.forms import NewPrescriptionForm

# Create your views here.
# Create new prescription view, this is the biz

class AddPrescriptionView(CreateView):
    template = 'new_rx.html'
    def get:
        form = NewPrescriptionForm
        return render(request, template ,{"form": form,})
    def post:
        form = NewPrescriptionForm(request.POST)
        if form.is_valid():
            print "yes"
        return render(request, template ,{"data": prescription_data})
