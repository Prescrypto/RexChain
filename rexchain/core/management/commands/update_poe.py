from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Q

from blockchain.models import Block
from blockchain.utils import PoE

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        '''This method verify that all the merkleroots in Dash Blockchain'''
        self.stdout.write("Starting update PoE")
        blocks = Block.objects.filter(Q(poetxid="False") | Q(poetxid=""))
        _poe = PoE()
        count = 0
        total_blocks = blocks.count()

        for block in blocks:
            block_poe = _poe.journal(block.merkleroot)
            if block_poe:
                block.poetxid = "True"
                count = count + 1
            else:
                block.poetxid = "False"
            # Save
            block.save()
            self.stdout.write('Updated merkleroot of this block hash: {}, in Dash Blockchain'.format(block.hash_block))

        self.stdout.write("Finish update PoE, total blocks updated: {} of {}".format(count, total_blocks))

    