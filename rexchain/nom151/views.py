""" Nom151 Views """
from django.shortcuts import render, redirect

from core.helpers import logger
from core.connectors import ReachCore

from .models import ConservationCertificate


def validate_certificate(request, merkleroot):
    """ Validates a hash_id """
    template = "nom151/validate.html"
    try:
        conservation_certificate = ConservationCertificate.objects.get(reference=merkleroot)
        # TODO add logic to get the tx id
    except Exception as e:
        logger.error(F"[Hash not found] : {merkleroot}, e: {e}")
        return redirect("home")
    else:
        nom151 = ReachCore()
        certificate = conservation_certificate.raw_document
        validate = nom151.validate(certificate, merkleroot)
        # TODO Handle if empty validate was found
        context = {
            "b": conservation_certificate.block,
            "validate": validate
        }
        return render(request, template, context)
