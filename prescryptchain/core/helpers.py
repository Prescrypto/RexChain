# -*- encoding: utf-8 -*-
''' Helper tools for rxchain '''
import logging
from django_rq import job
from django.core.cache import cache

def safe_set_cache(key, value):
    ''' Just kind '''
    logger = logging.getLogger('django_info')
    try:
        cache.set(key, value)
        cache.persist(key)
        logger.info('[SUCCESS]Saving redis key:{}, value:{}'.format(key, value))
    except Exception as e:
        logger.error('[ERROR SET variables on Redis]: {}, type:{}'.format(e, type(e)))
        raise e

