"""
Begins TEST API
"""
import logging
from django.test import TestCase

from rest_framework.test import APIClient
# from rest_framework.authtoken.models import Token

logger = logging.getLogger('django_info')


class RexchainBaseTestCase(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        # Test definitions
        self.client = self._authenticate()
        self.content_type = 'application/json'
        self.format = 'json'

    def _authenticate(self):
        """ Perform API Client Here! """
        client = APIClient()
        return client


class TestGetLastTransactions(RexchainBaseTestCase):

    def test_last_transactions(self):
        logger.info("Starting Test on Last Transactions")
        r = self.client.get('/api/v1/rx-endpoint/')
        self.assertEqual(r.status_code, 200)

    def test_block_list(self):
        logger.info("Starting Test on Block List")
        r = self.client.get('/api/v1/block/')
        self.assertEqual(r.status_code, 200)
