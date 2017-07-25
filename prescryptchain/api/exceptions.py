# -*- encoding: utf-8 -*-
from rest_framework.exceptions import APIException

class EmptyMedication(APIException):
    status_code = 400
    default_detail = 'No se puede enviar medicamentos sin nombre o que no pertenezca a un cuadro básico'
    default_code = 'Medications does not allow empty data'