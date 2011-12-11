#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       website.py
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


import abc
import sys
import csv
import urlparse
import urllib2

import os
import collections
import itertools
import time

import workerconsumerpool as wcp
import pagecounter
import stableurlopen

from workerconsumerpool import Worker              as ContentHandler
from lxml.html          import document_fromstring as parser


def stripped (func):
    def handled (*args):
        return func(*args).strip()
    return handled



class Site (object):


    @staticmethod
    def get_page_content (url):
        page = stableurlopen.urlopen(url)
        if page is None:
            return None
        content = page.read()
        page.close()
        return content


    @abc.abstractmethod
    def get_content_handler (self, results):
        pass


    @abc.abstractmethod
    def get_elements (self, document):
        pass


    def __init__ (
        self,
        domain,
        pagination,
        csv_header       = None,
        pagination_start = 1,
        tries            = 3,
        output           = None
    ):
        self.domain       = domain
        self.pagination   = pagination
        self.page_counter = pagecounter.PageCounter(
            self.construct_url(pagination),
            pagination_start
        )
        self.csv_header   = csv_header
        self.output_file  = os.extsep.join((domain, 'csv')) \
            if output is None \
            else output
        self.task_name    = domain
        self.tries        = tries

        __metaclass__ = abc.ABCMeta


    def handle (self):
        content_results = []
        if self.csv_header is not None:
            content_results.append(self.csv_header)

        print 'Handling {0}'.format(self.task_name)
        print '{0} pages to handle'.format(self._get_pagecount())
        for page in xrange(self.page_counter.left_bound, self._get_pagecount()):
            #        for page in xrange(1, 3):
            content_results.extend(self._parse_linkpage(page))
            time.sleep(1) # to avoid banning from a website side
        content_results.sort(key = lambda field: field[0])
        self._save(content_results)


    def _parse_linkpage (self, page_number):
        url = self.page_counter.construct_url(page_number)

        print '    {0} [{1:.2%}]'.format(
            url,
            self._get_percentage(page_number)
        )
        try:
            page = self.get_page_content(url)
        except urllib2.HTTPError as e:
            sys.stderr.write(
                "!!! Page '{0}' is unavailable [{1.code}]".format(page, e)
            )
            return

        results = collections.deque()
        handlers = wcp.Pool(self.get_content_handler(results))
        for el in self.get_elements(parser(page)):
            handlers.add(el)
        handlers.process()

        return results


    def _save (self, content):
        prepared = itertools.imap(
            lambda tupl: tuple(unicode(x).encode('utf-8') for x in tupl),
            content
        )
        try:
            with open(self.output_file, 'wb') as output:
                csv.writer(output).writerows(prepared)
        except IOError:
            sys.stder.write('Cannot handle with {0}'.format(self.output_file))
            sys.exit(1)


    def _get_pagecount (self):
        return self.page_counter.get_max_pagenumber()


    def _get_percentage (self, number):
        return float(number) / self._get_pagecount()


    def construct_url (self, *parts):
        return urlparse.urlunsplit(
            ('http', self.domain, '/'.join(parts), '', '')
        )
