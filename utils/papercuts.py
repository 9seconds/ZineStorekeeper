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



import re
import datetime

from dateutil.parser import parse as dateparse
from random          import expovariate as rnd
from gevent          import sleep
from urllib2         import urlopen as liburlopen, HTTPError, URLError
from sys             import stderr
from httplib         import HTTPException
from itertools       import imap



TRIES            = 3
MIN_TIME         = .2
MEAN_TIME        = 1
TEMP_ERROR_CODES = frozenset((
    403, 408, 409, 415, 417,
    500, 501, 502, 503, 504, 507, 509
))
RUENG_MONTHS = {
    u'января'   : u'january',
    u'февраля'  : u'february',
    u'марта'    : u'march',
    u'апреля'   : u'april',
    u'мая'      : u'may',
    u'июня'     : u'june',
    u'июля'     : u'july',
    u'августа'  : u'august',
    u'сентября' : u'september',
    u'октября'  : u'october',
    u'ноября'   : u'november',
    u'декабря'  : u'december',

    u'январь'   : u'january',
    u'февраль'  : u'february',
    u'март'     : u'march',
    u'апрель'   : u'april',
    u'май'      : u'may',
    u'июнь'     : u'june',
    u'июль'     : u'july',
    u'август'   : u'august',
    u'сентябрь' : u'september',
    u'октябрь'  : u'october',
    u'ноябрь'   : u'november',
    u'декабрь'  : u'december'
}
YEAR_PATTERN = re.compile('(?:(?:19)|(?:20))\d{2}', re.UNICODE)
YEAR_TODAY   = datetime.datetime.today().year


class HTTP404 (HTTPError):

    def __init__ (self):
        self.code = 404



##############
# Decorators #
##############



def stripped (func):
    def handled (*args):
        return func(*args).strip()

    return handled


def exceptionable (func):
    def handled (*args):
        try:
            return func(*args)
        except Exception as e:
            if __debug__:
                stderr.write('!!! There were the problem with {0} content handler.\n    Exception: {1}\n'.format(
                    func.__name__,
                    str(e)
                ))
            else:
                return ''

    return handled



#############
# Functions #
#############



def convert_date (dt, dayfirst = False, yearfirst = False, fuzzy = False):
    return dateparse(
        dt.strip(),
        dayfirst  = dayfirst,
        yearfirst = yearfirst,
        fuzzy     = fuzzy,
        ignoretz  = True
    ).strftime('%d.%m.%Y')


def convert_rudate (dt, dayfirst = False, yearfirst = False, fuzzy = True):
    date = u'{0} {1}'.format(dt, YEAR_TODAY) \
        if YEAR_PATTERN.search(dt) is None \
        else dt
    return convert_date(
        u' '.join(imap(
            lambda chunk: RUENG_MONTHS.get(chunk.lower(), chunk),
            date.split(u' ')
        )),
        dayfirst,
        yearfirst,
        fuzzy
    )






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
        except (HTTPException, URLError, IOError):
            rndsleep(MEAN_TIME*5)
