# -*- encoding: utf-8 -*-
''' Model behaviors functions that are repit between models '''
from django.db import models


class Timestampable(models.Model):
    ''' Abstract class for Timestampable created_at and updated_at '''

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
