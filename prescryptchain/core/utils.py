# -*- encoding: utf-8 -*-
''' Utils tools for rxchain '''

import time
import ast

from hashlib import sha256
from string import ascii_letters
from math import ceil, floor
from random import choice
from datetime import datetime, timedelta

from django.utils import timezone

class Hashcash(object):
    """ Main hashcash object """

    def __init__(self, debug=False, expiration_time="00:02:00", *args, **kwargs):
        """ Initialize hashcash object """
        self.tries = [0]
        self.date_format = "%m/%d/%Y %H:%M:%S"
        self.now = timezone.now
        self.debug = debug
        self.expiration_time = expiration_time

    def create_hashcash(
        self, word_initial, bits=20, long_from_chain=8):
        """Create a hashcash wiht three parameters.
        Parameters:
            word_initial: It is a type string value, with which it
            generates a challenge.
            bits: It is a type int value, indicates the dificulty
            that the proof of work(PoW) will have, we recommend using
            multiples of eight.
            long_form_chain: It is a type int value, is the long
            that a random chain in the hashcash.
        """
        ver = "Prescrypto1.0"
        date = self.now()
        #Change of format to date
        date = "{}.{}.{}.{}.{}.{}".format(
            str(date.month), str(date.day),
            str(date.year),str(date.hour),str(date.minute),str(date.second)
        )
        challenge = "{}*{}*{}*{}*{}*".format(
            ver, bits, date, word_initial,
            self._random_chain(long_from_chain)
        )
        hashcash = challenge + self.sha_calculus(challenge, bits)
        #return a string type
        return hashcash

    def sha_calculus(self, challenge, bits):
        """Calculus Sha256 a challenge with bits dificulty and returns
        the complement for challenger is True.
        Parameters:
            challenger:It is a type string value, with this value we
            apply sha256.
            bits:It is a type int value, indicates the dificulty that
            the proof of work(PoW) will have
        """
        counter = 0
        amount_zeros = int(ceil(bits/4.))
        zeros = '0'*amount_zeros
        while 1:
            with open('environ_rx_signal.txt', 'rb') as file:
                NEW_RX_SIGNAL = ast.literal_eval(str(file.readline()))

            if not NEW_RX_SIGNAL:
                if self.debug:
                    print('waiting new Rx signal')
                time.sleep(60*1)
                continue
            #Update to sha256
            sha = sha256(challenge + hex(counter)[2:]).hexdigest()
            if self.debug:
                print(sha)
            if sha[:amount_zeros] == zeros:
                self.tries[0] = counter
                if self.debug:
                    print("Number of attempts {}".format(counter))
                #return a string type
                return hex(counter)[2:]
            else:
                counter = counter + 1
                with open('environ_rx_signal.txt', 'wb') as file:
                    file.write('False')

    def check_hashcash(
            self, hashcash, word_initial=None, bits=None, time_expiration=True):
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
        #convert hashcash to a list
        hashcash_list = hashcash.split('*')
        #this block verifies if hashcash is correctly made
        if len(hashcash_list) != 6:
            print('Hashcash malformed')
            return False
        #Verifies that word_initial matches
        if word_initial is not None and word_initial != hashcash_list[3]:
            return False
        #Verify that bits matches
        if type(bits) is int and bits != int(hashcash_list[1]):
            return False
        #verify time of verification
        if time_expiration:
            today = self.now()
            today_clear = "{}/{}/{} {}:{}:{}".format(
                str(today.month), str(today.day), str(today.year),
                str(today.hour), str(today.minute), str(today.second)
            )
            today = datetime.strptime(today_clear, self.date_format)
            date = self._format_date(hashcash_list[2])
            date_expiration = self._add_date(date, self.expiration_time)
            verify = self._compare_dates(today_clear, date_expiration)
            #print(verify)
            #print(today)
            if verify == today:
                return False

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
        #return a string type
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
            #return a string type
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
            #return a datetime type
            return date2
        else:
            #return a datetime type
            return date1
