""" Nom151 related models  """
from django.db import models
from django.contrib.postgres.fields import JSONField

from core.behaviors import Timestampable


class ConservationCertificate(Timestampable, models.Model):
	""" This metadata is received by ReachCore identity as an official document for PoE """

	# Review if neccesary block relationship
	# block = models.OneToOneField('blockchain.Block', related_name='certificate', null=True, blank=True

	# Regular fields
	folio = models.CharField("Certificate Folio",
			max_length=255, blank=True, help_text='External Identifier')
	raw_document = models.TextField("Raw Certificate",
			blank=True, help_text='Base64 document')
	reference = models.CharField("Merkle Root used as reference",
			max_length=255, help_text='This ir our reference')

	# Metadata
	data = JSONField(default={}, blank=True)


	def __str__(self):
		""" Return custom string for the object
		raw_document first 6 digits then merkle_root first 6 digits too
		"""
		SLICE = 6
		return F"{self.raw_document[:SLICE]} - {self.reference[:6]}"




