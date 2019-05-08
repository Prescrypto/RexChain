# -*- encoding: utf-8 -*-
''' Util tools for RexChain '''
import logging

from hashlib import sha256
from string import ascii_letters
from math import ceil
from random import choice
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings


class Hashcash(object):
    """ Main hashcash object """

    def __init__(self, debug=settings.DEBUG, expiration_time="01:00:00", *args, **kwargs):
        """ Initialize hashcash object """
        self.logger = logging.getLogger('django_info')
        self.tries = [0]
        self.date_format = "%m/%d/%Y %H:%M:%S"
        self.now = timezone.now
        self.debug = debug
        self.expiration_time = expiration_time

    def create_challenge(
        self, word_initial, bits=int(settings.HC_BITS_DIFFICULTY),
        long_from_chain=int(settings.HC_RANDOM_STRING_SIZE)
    ):
        """Create a challenge wiht three parameters.
        Parameters:
            word_initial: It is a type string value, with which it
            generates a challenge.
            bits: It is a type int value, indicates the dificulty
            that the proof of work(PoW) will have, we recommend using
            multiples of eight.
            long_form_chain: It is a type int value, is the long
            that a random chain in the hashcash.
        """
        ver = "Prescrypto1.1"
        date = self.now()
        # Change of format to date
        date = "{}.{}.{}.{}.{}.{}".format(
            str(date.month), str(date.day), str(date.year),
            str(date.hour), str(date.minute), str(date.second),
        )
        challenge = "{}*{}*{}*{}*{}*".format(
            ver, bits, date, word_initial,
            self._random_chain(long_from_chain)
        )
        # Return a string type
        return challenge

    def calculate_sha(self, challenge, counter):
        """Calculates Sha256 a challenge
        Parameters:
            challenge: It is a type string, create for function create_challenge.
            counter: It is a type int, is the counter of tryes that we will do to find valid sha
        """
        bits = int(self._get_hashcash_bits(challenge))
        amount_zeros = int(ceil(bits/4.))
        zeros = '0'*amount_zeros
        valid_sha = False
        sha = sha256(challenge.encode() + hex(counter)[2:].encode()).hexdigest()
        if sha[:amount_zeros] == zeros:
            if self.debug:
                self.logger.info("[SUCCESS] SHA FOUND IT : {}".format(sha))
            valid_sha = True
        hashcash = "{}{}".format(challenge, hex(counter)[2:])
        # Return a list with True or False type and string type
        return valid_sha, hashcash

    def check_hashcash(
            self, hashcash, word_initial=None, bits=None, time_expiration=False):
        """Verify a Hashcash with three parameters
        Parameters:
            hashcash: It is a type string value, is the chain that is going
            to verify.
            word_intial: It is a type string value, this must match with the
            word_initial with which the hashcash was generated.
            bits: It is a type int value, this must match with the
            bits with which the hashcash was generated.
            time_expiration: If is True, add a time of expiration to hashcash.
        """
        # Convert hashcash to a list
        hashcash_list = hashcash.split('*')
        # This block verifies if hashcash is correctly made
        if len(hashcash_list) != 6:
            self.logger.error('Hashcash malformed')
            return False
        # Verifies that word_initial matches
        if word_initial is not None and word_initial != self._get_hashcash_word_initial(hashcash):
            return False
        # Verify that bits matches
        if type(bits) is int and bits != int(self._get_hashcash_bits(hashcash)):
            return False
        # Verify time of verification
        if time_expiration:
            today = self.now()
            today_clear = "{}/{}/{} {}:{}:{}".format(
                str(today.month), str(today.day), str(today.year),
                str(today.hour), str(today.minute), str(today.second)
            )
            today = datetime.strptime(today_clear, self.date_format)
            date = self._format_date(self._get_hashcash_date(hashcash))
            date_expiration = self._add_date(date, self.expiration_time)
            verify = self._compare_dates(today_clear, date_expiration)

            if verify == today:
                return False

        bits = int(self._get_hashcash_bits(hashcash))
        amount_zeros = int(ceil(bits/4.))
        # Return True or False: True==00134324525 or False==09321456799
        return sha256(hashcash).hexdigest().startswith('0'*amount_zeros)

    def _random_chain(self, long_from_chain):
        """Return a chain random
        Parameters:
            long_from_chain: It is a type int value, is the long that a
            random chain.
        """
        alphabet = ascii_letters + "+-/"
        # Return a string type
        return ''.join([choice(alphabet) for _ in [None]*long_from_chain])

    def _format_date(self, DATE):
        """Receive a string and give it a time format.
        Parameters:
            DATE: It is a type string value from the form "1.2.3.4.5.6"
        """
        date = DATE.split(".")
        if len(date) == 6:
            month = date[0]
            day = date[1]
            year = date[2]
            hours = date[3]
            minutes = date[4]
            seconds = date[5]
            format_date = "{}/{}/{} {}:{}:{}".format(
                month, day, year, hours, minutes, seconds
            )
            # Return a string type
            return format_date

    def _add_date(self, DATE, TIME):
        """Add an hour to a date.
        Parameters:
            DATE: It is a type string value from the form "01/23/45 67:89:01"
            TIME: It is a type string value from the form "67:89:01"
        """
        time = TIME.split(":")
        hours = int(time[0])
        minutes = int(time[1])
        seconds = int(time[2])
        # Convert to DATE a type datetime
        date = datetime.strptime(DATE, self.date_format)
        time_hours = timedelta(hours=hours)
        time_minutes = timedelta(minutes=minutes)
        time_seconds = timedelta(seconds=seconds)
        date_add_seconds = date + time_seconds
        date_add_minute = date_add_seconds + time_minutes
        date_add_hour = date_add_minute + time_hours
        date_add_time = date_add_hour.strftime(self.date_format)
        # Return a datetime type
        return date_add_time

    def _compare_dates(self, date1, date2):
        """Add an hour to a date.
        Parameters:
            date1: It is a type datetime value.
            date2: It is a type datetime value.
        """
        date1 = datetime.strptime(date1, self.date_format)
        date2 = datetime.strptime(date2, self.date_format)
        if date1 < date2:
            # Return a datetime type
            return date2
        else:
            # Return a datetime type
            return date1

    def _get_hashcash_version(self, hashcash):
        """Take the version in hashcash"""
        hashcash_list = hashcash.split('*')
        # Return a string type
        return hashcash_list[0]

    def _get_hashcash_bits(self, hashcash):
        """Take the bits in hashcash"""
        hashcash_list = hashcash.split('*')
        # Return a int type
        return int(hashcash_list[1])

    def _get_hashcash_date(self, hashcash):
        """Take the date in hashcash"""
        hashcash_list = hashcash.split('*')
        # Return a string type with format "HH.MM.SS"
        return hashcash_list[2]

    def _get_hashcash_word_initial(self, hashcash):
        """Take the word initial in hashcash"""
        hashcash_list = hashcash.split('*')
        # Return a string type
        return hashcash_list[3]

    def _get_hashcash_arrary_chain(self, hashcash):
        """Take the array chain in hashcash"""
        hashcash_list = hashcash.split('*')
        # Return a string type
        return hashcash_list[4]

    def _get_hashcash_counter(self, hashcash):
        """Take the hexadecimal of counter in hashcash"""
        hashcash_list = hashcash.split('*')
        # Return a string type
        return hashcash_list[5]

    def _get_calculation_sha(self, hashcash):
        """ Take a hashcash and calculate sha256 a hashcash"""
        sha = sha256(hashcash).hexdigest()
        # Return a string type
        return sha
