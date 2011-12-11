#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       stableurlopen.py
#
#       Copyright 2011 Serge Arkhipov <serge@aerialsounds.org>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#



from random import expovariate as rnd

import time
import urllib2



TRIES            = 3
MIN_TIME         = .1
MEAN_TIME        = .5
TEMP_ERROR_CODES = frozenset((
    403, 408, 409, 415, 417,
    500, 501, 502, 503, 504, 507, 509
))



class HTTP404 (urllib2.HTTPError):

    def __init__ (self):
        self.code = 404



def urlopen (url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        if e.code == 404:
            raise HTTP404
        elif e.code not in TEMP_ERROR_CODES:
            raise e
        else: # first attemp to retrieve resource was failed
            time.sleep(MIN_TIME + rnd(MEAN_TIME-MIN_TIME))
            for attempt in xrange(TRIES-1):
                try:
                    return urllib2.urlopen(url)
                except urllib2.HTTPError as e:
                    if e.code in TEMP_ERROR_CODES:
                        time.sleep(MIN_TIME + rnd(MEAN_TIME-MIN_TIME))
                    elif e.code == 404:
                        raise HTTP404
                    else:
                        raise e
