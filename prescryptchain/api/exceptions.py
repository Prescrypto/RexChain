# -*- encoding: utf-8 -*-
from rest_framework.exceptions import APIException

class EmptyMedication(APIException):
    status_code = 400
    default_detail = 'No se puede enviar medicamentos sin nombre o que no pertenezca a un cuadro básico'
    default_code = 'Medications does not allow empty data'


class FailedVerifiedSignature(APIException):
    status_code = 400
    default_detail = 'Fallo el chequeo de la firma, checa tu payload lo creaste bien o si no se enviaron tus datos corruptamente'
    default_code = 'Failed verified Signature'
