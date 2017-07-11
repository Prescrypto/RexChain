# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Block, Prescription, Medication


class PrescriptionAdmin(admin.ModelAdmin):
    ''' Custom Prescription Admin  '''
    search_fields = ['id']
    list_per_page = 25
    fields = ('id','public_key', 'medic_name', 'patient_name','timestamp')
    # inlines = [MedicationInline, ]


# Register your models here.
admin.site.register(Block)
admin.site.register(Prescription)
admin.site.register(Medication)