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
import contextlib
import urlparse
import urllib2
import lxml.html as parser
import os
import collections
import itertools

import workerconsumerpool as wcp
from workerconsumerpool import Worker as ContentHandler
import pagecounter



def stripped (func):
    def handled (*args):
        return func(*args).strip()
    return handled



class Site (object):

    def __init__ (self, domain, pagination, csv_header = None, pagination_start = 1, output = None):
        self.domain = domain
        self.pagination = pagination
        self.page_counter = pagecounter.PageCounter(self.construct_url(pagination), pagination_start)
        self.csv_header = csv_header
        self.output_file = os.extsep.join((domain, 'csv')) \
            if output is None else output

        __metaclass__ = abc.ABCMeta

    def construct_url (self, *parts):
        return urlparse.urlunsplit(('http', self.domain, '/'.join(parts), '', ''))

    def get_pagecount (self):
        return self.page_counter.get_max_pagenumber()

    @staticmethod
    def get_page_content (url):
        with contextlib.closing(urllib2.urlopen(url)) as page:
            return page.read()

    @abc.abstractmethod
    def get_content_handler (self, results):
        pass

    @abc.abstractmethod
    def get_elements (self, document):
        pass

    @staticmethod
    def get_parser (content):
        return parser.document_fromstring(content)

    def parse_linkpage (self, page_number):
        page = self.page_counter.construct_url(page_number)
        page_content = ''
        try:
            page_content = self.get_page_content(self.page_counter.construct_url(page_number))
        except urllib2.HTTPError as e:
            sys.stderr.write("Page '{0}' is unavailable [{1.code}]".format(page, e))
            return

        results = collections.deque()
        handlers = wcp.Pool(self.get_content_handler(results))
        for el in self.get_elements(self.get_parser(page_content)):
            handlers.add(el)
        handlers.process()

        return results

    def handle (self):
        content_results = []
        if not self.csv_header is None:
            content_results.append(self.csv_header)
#        for page in xrange(self.page_counter.left_bound, self.page_counter.get_max_pagenumber()):
        for page in xrange(1, 10):
            content_results.extend(self.parse_linkpage(page))
        content_results.sort(key = lambda field: field[0])
        self.save(content_results)

    def save (self, content):
        prepared = itertools.imap(lambda tupl: tuple(x.encode('utf-8') for x in tupl), content)

        try:
            with open(self.output_file, 'wb') as output:
                csv.writer(output).writerows(prepared)
        except IOError:
            sys.stder.write('Cannot handle with {0}'.format(self.output_file))
            sys.exit(1)
