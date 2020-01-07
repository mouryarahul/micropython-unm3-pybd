#! /usr/bin/env python
#
# MicroPython Simple Network for NM3
#
# This file is part of nm3-micropython-pybd derived from NM3 Python Driver. 
# https://github.com/bensherlock/nm3-micropython-pybd
# https://github.com/bensherlock/nm3-python-driver
#
#
# MIT License
#
# Copyright (c) 2020 Benjamin Sherlock <benjamin.sherlock@ncl.ac.uk>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""MicroPython Simple Network for the NM3."""

#from collections import deque

from .unm3driver import Nm3


class Nm3NetworkSimple:
    """NM3 Simple Network."""

    def __init__(self,
                 nm3_modem: Nm3):
        """Constructor. 
           """
        self._nm3_modem = nm3_modem
        

    def __call__(self):
        return self


    def send_message(self,
                     address: int,
                     message_bytes: bytes,
                     retries: int = 3,
                     timeout: float = 5.0) -> (float, int):
        """Sends a message of message_bytes to address. Maximum of 64 bytes.
           Retries on timeout - both are user configurable.
           Returns duration and number of retries, or -1 if failed.
        """

        # Checks on parameters
        if address < 0 or address > 255:
            print('Invalid address (0-255): ' + str(address))
            return -1

        if len(message_bytes) < 2 or len(message_bytes) > 64:
            print('Invalid length of message_bytes (2-64): ' + str(len(message_bytes)))
            return -1

        response_time = self._nm3_modem.send_unicast_message_with_ack(address, message_bytes)
        retries_count = retries
        while response_time < 0 and retries_count > 0:
            retries_count = retries_count - 1
            response_time = self._nm3_modem.send_unicast_message_with_ack(address, message_bytes)

        return (response_time, (retries_count-retries))

