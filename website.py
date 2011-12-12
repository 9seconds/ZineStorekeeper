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
import gc

import os
import collections
import itertools

import workerconsumerpool as wcp
import pagecounter
import utils

from lxml.html import document_fromstring as parser



def stripped (func):
    def handled (*args):
        return func(*args).strip()
    return handled



class Site (object):


    @abc.abstractmethod
    def get_page_data (self, content):
        pass


    @staticmethod
    def get_page_content (url):
        page = utils.urlopen(url)
        if page is None:
            return None
        content = page.read()
        page.close()
        return content


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
        self.csv_header  = csv_header
        self.output_file = os.extsep.join((domain, 'csv')) \
            if output is None \
            else output
        self.task_name = domain
        self.tries     = tries

        __metaclass__ = abc.ABCMeta


    def handle (self):
        content_results = []

        print 'Handling {0}'.format(self.task_name)
        print '{0} pages to handle'.format(self._get_pagecount())
        for page in xrange(self.page_counter.left_bound, self._get_pagecount()+1):
            content_results.extend(self._parse_linkpage(page))
            if page % 100 == 0: # make a cleaning every 100 pages
                gc.collect()
            utils.rndsleep(1) # to avoid banning from a website side
        content_results.sort(key = self.get_sorter)

        if self.csv_header is not None:
            content_results.insert(0, self.csv_header)

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
        if page is None:
            sys.stderr.write('*** Problems with {0}. Please check'.format(url))
            return

        results = collections.deque()
        handlers = wcp.Pool(self.get_content_handler(results))
        for el in self.get_elements(parser(page)):
            handlers.add(el)
        handlers.process()

        return results


    def get_content_handler (self, results):
        @wcp.Worker.Method
        def method (url):
            try:
                content = self.get_page_content(url)
                if content is None:
                    raise Exception
                data = self.get_page_data(
                    url,
                    parser(content).cssselect(self.css_content)[0]
                )
            except:
                method.panic('*** Problems with {0}. Please check.'.format(url))
                return None

            results.append(data)
        return method


    def get_elements (self, document):
        return itertools.imap(
            lambda el: self.construct_url(el),
            (el.get('href') for el in document.cssselect(self.css_elements))
        )


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


    def get_sorter (self, tupl):
        return tupl[0]


    def _get_pagecount (self):
        return self.page_counter.get_max_pagenumber()


    def _get_percentage (self, number):
        return float(number) / self._get_pagecount()


    def construct_url (self, *parts):
        return urlparse.urlunsplit(
            ('http', self.domain, '/'.join(parts), '', '')
        )
