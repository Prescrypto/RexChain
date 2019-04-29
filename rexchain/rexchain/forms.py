# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django import forms
from core.helpers import create_jira_issue

logger = logging.getLogger('django_info')


class AskCtaEmailForm(forms.Form):
    email = forms.EmailField(required=True)

    def send_jira_card(self):
        ''' Send jira card '''
        email = self.cleaned_data["email"]
        try:
            create_jira_issue(
                summary="500 Startup Colombia ask mail CTA: {}".format(email),
                description='This user ask for more info in landingpage: {}'.format(email))
        except Exception as e:
            logger.error("[AskCTAEMAIL JIRA ERROR]: {}".format(e))
