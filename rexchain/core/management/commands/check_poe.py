from django.core.management.base import BaseCommand
from django.core.cache import cache

from blockchain.models import Block
from blockchain.utils import PoE

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        '''This method check if the merkleroot in Dash Blockchain'''
        self.stdout.write("Starting check PoE of blocks without poetxid")
        blocks = Block.objects.filter(poetxid="True")
        _poe = PoE()
        count = 0

        for block in blocks:
            block_poe = _poe.attest(block.merkleroot)
            if block_poe['code'] == 302:
                block.poetxid = block_poe['transactionID']
                block.save()
                count = count + 1
                self.stdout.write("Saved Dash txid in block wiht hash: {}".format(block.hash_block))

        self.stdout.write("Finish update PoE, total blocks updated: {}".format(count))

