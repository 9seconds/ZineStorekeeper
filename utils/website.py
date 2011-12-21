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

from lxml.html import document_fromstring as parser, tostring as parser_str
from locale    import LC_ALL, setlocale
from urlparse  import urlunsplit
from itertools import imap
from sys       import stderr, exit
from csv       import writer as csvwriter
from abc       import abstractmethod, ABCMeta as Abstract
from os        import extsep

from . import workerconsumerpool as wcp
from . import pagecounter

from .papercuts import urlopen, rndsleep, HTTPError




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


    @staticmethod
    def get_page_content (url):
        page = urlopen(url)
        if page is None:
            return None
        content = page.read()
        page.close()
        return content


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
        loc              = 'en_US',
        output           = None
    ):
        self.domain       = domain
        self.pagination   = pagination
        self.page_counter = pagecounter.PageCounter(
            self.construct_url(pagination),
            pagination_start
        )
        self.csv_header = csv_header
        self.output     = output
        self.task_name  = domain
        self.tries      = tries
        self.loc        = loc

        __metaclass__ = Abstract


    def handle (self):
        content_results = []

        setlocale(LC_ALL, self.loc)

        print 'Handling {0}'.format(self.task_name)
        print '{0} pages to handle'.format(self.get_pagecount())
        #for page in xrange(self.page_counter.left_bound, self.get_pagecount()+1):
        for page in xrange(self.page_counter.left_bound, 3):
            parse_results = None
            for attempt in xrange(self.tries):
                parse_results = self._parse_linkpage(page)
                if parse_results is not None:
                    break
            else:
                stder.write('Cannot handle with {0}'.format(self.output_file))
                exit(1)

            content_results.extend(parse_results)

            rndsleep(.5) # to avoid banning from a website side
        content_results.sort(key = self.get_sorter)

        if self.csv_header is not None:
            content_results.insert(0, self.csv_header)

        self._save(content_results)

        setlocale(LC_ALL, 'C')


    def _parse_linkpage (self, page_number):
        url = self.page_counter.construct_url(page_number)

        print '    {0} [{1:.2%}]'.format(
            url,
            float(page_number) / self.get_pagecount()
        )
        try:
            page = self.get_page_content(url)
        except HTTPError as e:
            stderr.write(
                "!!! Page '{0}' is unavailable [{1.code}]".format(page, e)
            )
            return None
        if page is None:
            stderr.write('*** Problems with {0}. Please check'.format(url))
            return None

        return self.start_parse_linkpage(parser(page))


    def _save (self, content):
        prepared = imap(
            lambda tupl: tuple(unicode(x).encode('utf-8') for x in tupl),
            content
        )
        try:
            with open(self._get_output_filename(), 'wb') as output:
                csvwriter(output).writerows(prepared)
        except IOError:
            stder.write('Cannot handle with {0}'.format(self.output_file))
            exit(1)


    def _get_output_filename (self):
        return self.output \
            if self.output is not None \
            else extsep.join((self.task_name.replace(' ', extsep), 'csv'))


    def get_pagecount (self):
        return self.page_counter.get_max_pagenumber()


    def construct_url (self, *parts):
        return urlunsplit( ('http', self.domain, '/'.join(parts), '', '') )



class OneStep (Generic):


    def __init__ (
        self,
        domain,
        pagination,
        csv_header       = None,
        pagination_start = 1,
        tries            = 3,
        output           = None
    ):
        super(OneStep, self).__init__(
            domain,
            pagination,
            csv_header,
            pagination_start,
            tries,
            output
        )


    def start_parse_linkpage (self, page):
        results = []
        for el in self.get_elements(page):
            results.append(self.handle_element(el))

        return results


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
        output           = None
    ):
        super(TwoStep, self).__init__(
            domain,
            pagination,
            csv_header,
            pagination_start,
            tries,
            output
        )


    def start_parse_linkpage (self, page):
        results = []
        handlers = wcp.Pool(self.get_content_handler(results))
        for el in self.get_elements(page):
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
                results.append(self.get_page_data(
                    url,
                    parser(content).cssselect(self.css_content)[0]
                ))
            except Exception as e:
                if __debug__:
                    print '!!! ' + str(e)

                method.panic('*** Problems with {0}. Please check.'.format(url))
                return None

        return method


    def get_elements (self, document):
        return imap(
            lambda el: self.construct_url(el),
            ( el.get('href') for el in document.cssselect(self.css_elements) )
        )


    def get_sorter (self, tupl):
        return tupl[1] + tupl[2]
