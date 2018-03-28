# -*- encoding: utf-8 -*-
''' Helper tools for rxchain '''
import logging
from django_rq import job


@job
def say_hello(name="World"):
    ''' Just kind '''
    logger = logging.getLogger('django_info')
    logger.info("Hello {}".format(name))
