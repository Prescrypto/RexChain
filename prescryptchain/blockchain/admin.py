# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Block, Prescription, Medication

# Register your models here.
admin.site.register(Block)
admin.site.register(Prescription)
admin.site.register(Medication)