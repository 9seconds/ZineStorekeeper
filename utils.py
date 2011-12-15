#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       utils.py
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


from dateutil.parser import parse as dateparse
from random          import expovariate as rnd
from time            import sleep
from urllib2         import urlopen as liburlopen, HTTPError, URLError



TRIES            = 3
MIN_TIME         = .1
MEAN_TIME        = .5
TEMP_ERROR_CODES = frozenset((
    403, 408, 409, 415, 417,
    500, 501, 502, 503, 504, 507, 509
))



class HTTP404 (HTTPError):

    def __init__ (self):
        self.code = 404


def convert_date (dt, dayfirst = False, yearfirst = False, fuzzy = False):
    return dateparse(
        dt.strip(),
        dayfirst  = dayfirst,
        yearfirst = yearfirst,
        fuzzy     = fuzzy,
        ignoretz  = True
    ).strftime('%m/%d/%Y')


def rndsleep (mean_time = MEAN_TIME, min_time = MIN_TIME):
    sleep(MIN_TIME + rnd(MEAN_TIME-MIN_TIME))


def urlopen (url):
    for attempt in xrange(TRIES):
        try:
            return liburlopen(url)
        except HTTPError as e:
            if e.code == 404:
                raise HTTP404
            elif e.code in TEMP_ERROR_CODES:
                rndsleep()
            else:
                raise e
        except URLError as e:
            pass
