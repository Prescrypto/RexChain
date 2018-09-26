# -*- encoding: utf-8 -*-
''' Helper tools for RexChain '''
import logging
import time
from django_rq import job
from django.core.cache import cache

def safe_set_cache(key, value):
    ''' Just kind '''
    logger = logging.getLogger('django_info')
    try:
        cache.set(key, value)
        cache.persist(key)
        logger.info('[SUCCESS] Saving in redis key:{}, value:{}'.format(key, value))
    except Exception as e:
        logger.error('[ERROR SET variables on Redis]: {}, type:{}'.format(e, type(e)))
        raise e


def get_timestamp(date_to_convert):
    ''' Take a datetime and convert to timestamp '''
    logger = logging.getLogger('django_info')
    try:
        return int(round(time.mktime(date_to_convert.timetuple())*1000))
    except Exception as e:
        logger.error('[ERROR Get timestamp]: {}, type:{}'.format(e, type(e)))
        return None
