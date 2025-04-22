# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python libs
import json
import logging

# Django packages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
# Our Models
from django.conf import settings
from .models import Payload, Block, Transaction
# Blockcypher
from api.views import PayloadSerializer

logger = logging.getLogger('django_info')


class ValidateRxView(View):
    ''' Validate PoE of one Transaction with a block
        poe.received Date of stampd
        poe.poe_url Url of PoE
        poe.hash Hash of PoE Transaction
        poe.data_hex Data Hex
        merkle_root Merkle Root of block
    '''

    template = "blockchain/validate.html"

    def get(self, request, *args, **kwargs):
        hash_id = kwargs.get("hash_id")
        payload = tx = None
        template = "blockchain/validate.html"
        try:
            payload = Payload.objects.get(hash_id=hash_id)
            tx = payload.transaction
        except Exception as e:
            logger.info("[Validate ERROR]:{} type:{}".format(e, type(e)))
            # Try to get from transaction ID
            try:
                tx = Transaction.objects.get(txid=hash_id)
            except Exception as e:
                _message_error = "[Validate ERROR] Neither hash is from Payload nor Transaction:{} type:{}"
                logger.error(_message_error.format(e, type(e)))
                return redirect("/")
        return render(request, template, {"tx": tx})


def glossary(request):
    ''' Proof of existence explanation '''
    return render(request, "blockchain/glossary.html")


def tx_detail(request, hash_id=False):
    ''' Get a hash and return the blockchain model '''
    if request.GET.get("hash_id", False):
        hash_id = request.GET.get("hash_id")

    if hash_id:
        context = dict()
        try:
            rx = Payload.objects.get(hash_id=hash_id)
        except:  # noqa : F841
            try:
                # This line filters Payload objects based on the 'txid' of the
                # related Transaction object. The double underscore ('__')
                # signifies a lookup across the ForeignKey relationship
                # ('transaction'). This translates to the SQL query with the
                # INNER JOIN and the WHERE clause on blockchain_transaction.txid.
                # For this reason, we use an index on Transaction.txid
                rx = Payload.objects.get(transaction__txid=hash_id)
            except Exception as e:
                logger.error("Error :{}, type({})".format(e, type(e)))
                return redirect("/block/?block_hash={}".format(hash_id))

        _payload = PayloadSerializer(rx)

        context.update({
            "rx": rx,
            "payload": json.dumps(_payload.data, sort_keys=True, indent=4, ensure_ascii=False),
        })
        return render(request, "blockchain/rx_detail.html", context)

    return redirect("/")


def rx_priv_key(request, hash_rx=False):
    # Temporary way to show key just for test, remove later
    try:
        rx = Payload.objects.get(hash_id=hash_rx)
        return HttpResponse(rx.get_priv_key, content_type="text/plain")
    except Exception as e:  # noqa: F841
        return HttpResponse("Not Found", content_type="text/plain")


def block_detail(request, block_hash=False):
    ''' Get a hash and return the block'''
    if request.GET.get("block_hash", False):
        block_hash = request.GET.get("block_hash")

    if block_hash:
        context = {}
        try:
            block = Block.objects.get(hash_block=block_hash)
            context["block_object"] = block
            if block.poetxid == "True":
                context["message_poe"] = "PoE en proceso"
            elif block.poetxid == "False" or block.poetxid.strip() == "":
                context["message_poe"] = "Sin PoE por el momento"
            elif block.poetxid == "Genesis":
                context["message_poe"] = "Block Genesis"
            else:
                # Create URL
                context["poe_url"] = "{}/dash/tx/{}/".format(settings.BASE_POE_URL, block.poetxid)
                context["message_poe"] = "PoE válida"

            return render(request, "blockchain/block_detail.html", context)

        except Exception as e:
            logger.error("Error found: {}, type: {}".format(e, type(e)))

    return redirect("/")
