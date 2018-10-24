# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Block, Payload


class PayloadAdmin(admin.ModelAdmin):
    ''' Custom Payload Admin  '''
    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    search_fields = ['id']
    list_per_page = 25
    fields = ('id','public_key','timestamp',)
    exclude = ('public_key', )
    readonly_fields = ("public_key", "private_key", "data", "signature")


admin.site.register(Block)
admin.site.register(Payload)
