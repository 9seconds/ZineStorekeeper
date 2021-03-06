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


import plugins

import multiprocessing

from lxml.html   import document_fromstring as parser, tostring as parser_str
from urlparse    import urlunsplit
from itertools   import ifilter, imap, chain
from sys         import stderr, exit
from csv         import writer as csvwriter
from abc         import abstractmethod, ABCMeta as Abstract
from os          import extsep
from gevent.pool import Pool
from chardet     import detect as charset_detect
from collections import deque

from .          import pagecounter
from .papercuts import urlopen, HTTP404



CPU_COUNT    = multiprocessing.cpu_count()
GLOBAL_COUNT = 3*CPU_COUNT
ALL_COUNT    = GLOBAL_COUNT**2



class Generic (object):


    @abstractmethod
    def get_sorter (self, tupl):
        pass


    @abstractmethod
    def get_page_data (self, content):
        pass


    @abstractmethod
    def start_parse_linkpage (self, page):
        pass


    @classmethod
    def register (cls):
        plugins.register(cls, cls.__name__.lower())


    def __init__ (
        self,
        domain,
        pagination,
        csv_header       = None,
        pagination_start = 1,
        tries            = 3,
        encoding         = None,
        output           = None
    ):
        self.domain       = domain
        self.pagination   = pagination
        self.page_counter = pagecounter.PageCounter(
            self.construct_url(pagination),
            pagination_start
        )
        self.csv_header   = csv_header
        self.output       = output
        self.task_name    = domain
        self.tries        = tries
        self.global_pool  = Pool(GLOBAL_COUNT)
        self.element_pool = Pool(ALL_COUNT)

        if encoding == 'auto':
            self.charset_decoder = lambda s: s.decode(charset_detect(s)['encoding'].lower())
        elif encoding is not None:
            self.charset_decoder = lambda s: s.decode(encoding.lower())
        else:
            self.charset_decoder = lambda s: s

        __metaclass__ = Abstract


    def handle_page_unit (self, unit):
        for attempt in xrange(self.tries):
            parse_results = self.parse_linkpage(unit)
            if parse_results is not None:
                return parse_results
        else:
            stderr.write('Cannot handle with {0}'.format(unit))
            exit(1)


    def handle (self):
        results = deque()

        elements = chain.from_iterable(self.global_pool.imap_unordered(
            self.handle_page_unit,
            self.get_progress()
        ))

        self.element_pool.map(
            lambda url: self.parse_page(url, results),
            elements
        )

        content = sorted(filter(None, results), key = self.get_sorter)

        if self.csv_header is not None:
            content.insert(0, self.csv_header)

        self.save(content)


    def parse_page (self, url, results):
        for attempt in xrange(self.tries):
            try:
                results.append(self.start_parse_page(
                    url,
                    parser(self.get_page_content(url))
                ))
            except ValueError: # if self.get_page_content returns None and parser dies
                pass
            except (HTTP404, IndexError): # IndexError raised by lxml.etree in order if parsing was unsuccessful
                print 'Some problems with {0}. Please check'.format(url)
        else:
            print 'Some problems with {0}. Please check'.format(url)


    def get_page_content (self, url):
        page = urlopen(url)
        if page is None:
            return None
        content = page.read()
        page.close()

        return self.charset_decoder(content)


    def save (self, content):
        prepared = imap(
            lambda tupl: tuple(unicode(x).encode('utf-8') for x in tupl),
            content
        )
        try:
            with open(self.get_output_filename(), 'wb') as output:
                csvwriter(output).writerows(prepared)
        except IOError:
            stder.write('Cannot handle with {0}'.format(self.output_file))
            exit(1)


    def get_output_filename (self):
        return self.output \
            if self.output is not None \
            else extsep.join((self.task_name.replace(' ', extsep), 'csv'))


    def get_pagecount (self):
        return self.page_counter.get_max_pagenumber()


    def construct_url (self, *parts):
        return urlunsplit( ('http', self.domain, '/'.join(parts), '', '') )


    def get_progress (self, left_bound = None, right_bound = None):
        lb = left_bound  if left_bound is not None  else self.page_counter.left_bound
        rb = right_bound if right_bound is not None else self.get_pagecount()

        return xrange(lb, rb+1)


    def get_empty_tuple (self):
        return tuple()








class OneStep (Generic):


    def __init__ (
        self,
        domain,
        pagination,
        csv_header       = None,
        pagination_start = 1,
        tries            = 3,
        encoding         = None,
        output           = None
    ):
        super(OneStep, self).__init__(
            domain,
            pagination,
            csv_header,
            pagination_start,
            tries,
            encoding,
            output
        )


    def handle_page_unit (self, unit):
        return (self.page_counter.construct_url(unit),)


    def start_parse_page (self, url, page):
        return ( self.handle_element(el) for el in self.get_elements(page) )


    def get_sorter (self, tupl):
        return tupl[0]








class TwoStep (Generic):


    def __init__ (
        self,
        domain,
        pagination,
        csv_header       = None,
        pagination_start = 1,
        tries            = 3,
        encoding         = None,
        output           = None
    ):
        super(TwoStep, self).__init__(
            domain,
            pagination,
            csv_header,
            pagination_start,
            tries,
            encoding,
            output
        )


    def handle_page_unit (self, unit):
        url  = self.page_counter.construct_url(unit)

        try:
            return self.get_elements(parser( self.get_page_content(url) ))
        except HTTPError as e:
            stderr.write(
                "!!! Page '{0}' is unavailable [{1.code}]".format(url, e)
            )
        if page is None:
            stderr.write('*** Problems with {0}. Please check'.format(url))

        return tuple()


    def start_parse_page (self, url, page):
        return (self.get_page_data(
            url,
            page.cssselect(self.css_content)[0]
        ),)


    def get_elements (self, document):
        return imap(
            lambda el: self.construct_url(el),
            ( el.get('href') for el in document.cssselect(self.css_elements) )
        )


    def get_sorter (self, tupl):
        return tupl[1] + tupl[2]
