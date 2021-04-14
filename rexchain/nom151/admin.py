from django.contrib import admin

from .models import ConservationCertificate


class ConservationCertificateAdmin(admin.ModelAdmin):
    pass


admin.site.register(ConservationCertificate, ConservationCertificateAdmin)
