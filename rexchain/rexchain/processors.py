# -*- encoding: utf-8 -*-
# Define custom processors to all templates
from django.conf import settings


def add_production_var(request):
    ''' add production var to templates '''
    return {
        "PRODUCTION": settings.PRODUCTION,
        "WALLET_URL": settings.WALLET_URL,
        "WHITEPAPER_URL": settings.WHITEPAPER_URL,
    }
