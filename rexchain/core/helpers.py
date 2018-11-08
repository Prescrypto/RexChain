# -*- encoding: utf-8 -*-
''' Helper tools for RexChain '''
import logging
import time
from django_rq import job
from django.core.cache import cache
from django.conf import settings

from jira import JIRA

logger = logging.getLogger('django_info')

def safe_set_cache(key, value):
    ''' Just kind '''
    try:
        cache.set(key, value)
        cache.persist(key)
        logger.info('[SUCCESS] Saving in redis key:{}, value:{}'.format(key, value))
    except Exception as e:
        logger.error('[ERROR SET variables on Redis]: {}, type:{}'.format(e, type(e)))
        raise e


def get_timestamp(date_to_convert):
    ''' Take a datetime and convert to timestamp '''
    try:
        return int(round(time.mktime(date_to_convert.timetuple())*1000))
    except Exception as e:
        logger.error('[ERROR Get timestamp]: {}, type:{}'.format(e, type(e)))
        return None


def create_jira_issue(summary, description, comment="", project_key="PROP", task_type="Task"):
    # Method to create JIRA issue
    try:
        authed_jira = JIRA(server=settings.JIRA_URL, basic_auth=(settings.JIRA_USER, settings.JIRA_PASSWORD))
        issue_dict = {
            'project': {'key': project_key},
            'description': description,
            'issuetype': {'name': task_type},
            'summary' : summary,
        }
        if not settings.PRODUCTION:
            issue_dict["project"] = {'key' : 'DEVPROP'}
            issue_dict["summary"] = '[DEV] ' + summary

        new_issue = authed_jira.create_issue(fields=issue_dict)
        # add comments
        if comment != "":
            authed_jira.add_comment(new_issue, comment)

    except Exception as e:
        logger.error( "Error al Crear Issue en JIRA : {}.".format(e))
