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
from .utils import get_qr_code
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
        payload = transaction = None
        try:
            payload = Payload.objects.get(hash_id=hash_id)
        except Exception as e:
            logger.info("[Validate ERROR]:{} type:{}".format(e, type(e)))
            # Try to get from transaction ID
            try:
                transaction = Transaction.objects.get(txid=hash_id)
            except Exception as e:
                _message_error = "[Validate ERROR] Neither hash is from Payload nor Transaction:{} type:{}"
                logger.error(_message_error.format(e, type(e)))
            else:
                return render(request, self.template, {"poe": self.get_poe_data_context(transaction)})
        else:
            poe = self.get_poe_data_context(payload.transaction)
            return render(request, self.template, {"poe": poe})

        return redirect("/")

    def get_poe_data_context(self, transaction):
        ''' Build poe data '''
        # Transaction TEST for validate TESTING only
        data_poe = {
            "received": "Aug. 25, 2018, 12:57 p.m.",
            "poe_url": ("https://live.blockcypher.com/bcy/tx/"
                        "51998b337855f999718f3be0658af19f1615dd71dd8885a24e6c08bf201c257a/"),
            "hash": "51998b337855f999718f3be0658af19f1615dd71dd8885a24e6c08bf201c257a",
            "data_hex": "46e6ac758721c8f45d2a00de78d81df7861f655e41777f8e56b0556ea4bec0a9",
            "merkle_root": "46e6ac758721c8f45d2a00de78d81df7861f655e41777f8e56b0556ea4bec0a9",
        }

        if transaction.block_id:
            block = transaction.block

            if block.poetxid.strip() in ["True", "False", "", "Genesis"]:
                pass
            else:
                try:
                    data_poe = {
                        "received": block.timestamp.strftime('%Y-%m-%d'),
                        "poe_url": "{}/dash/tx/{}/".format(settings.BASE_POE_URL, block.poetxid),
                        "hash": block.poetxid,
                        "data_hex": block.merkleroot,
                        "merkle_root": block.merkleroot,
                    }

                except Exception as e:
                    logger.info("[Get Poe Data ERROR]:{} type:{}".format(e, type(e)))

        return data_poe


def poe(request):
    ''' Proof of existence explanation '''
    return render(request, "blockchain/poe.html")


def tx_detail(request, hash_id=False):
    ''' Get a hash and return the blockchain model '''
    if request.GET.get("hash_id", False):
        hash_id = request.GET.get("hash_id")

    if hash_id:
        context = dict()
        try:
            rx = Payload.objects.get(hash_id=hash_id)
        except Exception as e:
            try:
                rx = Payload.objects.get(transaction__txid=hash_id)
            except Exception as e:
                print("Error :%s, type(%s)" % (e, type(e)))
                return redirect("/block/?block_hash=%s" % hash_id)

        _payload = PayloadSerializer(rx)

        context.update({
            "rx": rx,
            "payload": json.dumps(_payload.data, sort_keys=True, indent=4),
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


def qr_code(request, hash_rx=False):
    # Temporary way to show qrcode just for test, remove later
    try:
        rx = Payload.objects.get(hash_id=hash_rx)
        img = get_qr_code(rx.get_priv_key)
        return HttpResponse(img, content_type="image/jpeg")
    except Exception as e:
        print("Error :%s, type(%s)" % (e, type(e)))
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
            print("Error found: %s, type: %s" % (e, type(e)))

    return redirect("/")
