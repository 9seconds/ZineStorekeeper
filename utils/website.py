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

from lxml.html   import document_fromstring as parser, tostring as parser_str
from locale      import LC_ALL, setlocale
from urlparse    import urlunsplit
from itertools   import imap
from sys         import stderr, exit
from csv         import writer as csvwriter
from abc         import abstractmethod, ABCMeta as Abstract
from os          import extsep
from collections import deque

from .          import pagecounter, progress
from .papercuts import urlopen, rndsleep, HTTPError

from gevent.pool import Pool




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


    def handle_page_unit (self, unit):
        parse_results = None
        for attempt in xrange(self.tries):
            parse_results = self._parse_linkpage(unit)
            if parse_results is not None:
                return parse_results
        else:
            stder.write('Cannot handle with {0}'.format(unit))
            exit(1)



    def handle (self):
        content_results = []

        setlocale(LC_ALL, self.loc)

        #for page in xrange(self.page_counter.left_bound, self.get_pagecount()+1):
        #for page in self.get_page_range(right_bound = 3):
        work = self.get_progress(right_bound = 20)
        for page in work:
            work.set_dynamic(page)

            parse_results = None
            for attempt in xrange(self.tries):
                parse_results = self._parse_linkpage(page)
                if parse_results is not None:
                    break
            else:
                stder.write('Cannot handle with {0}'.format(self.output_file))
                exit(1)

            content_results.extend(parse_results)

            #rndsleep(.5) # to avoid banning from a website side
        content_results.sort(key = self.get_sorter)

        if self.csv_header is not None:
            content_results.insert(0, self.csv_header)

        self._save(content_results)

        setlocale(LC_ALL, 'C')


    def _parse_linkpage (self, page_number):
        url = self.page_counter.construct_url(page_number)

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


    def get_progress (self, left_bound = None, right_bound = None):
        lb = left_bound  if left_bound is not None  else self.page_counter.left_bound
        rb = right_bound if right_bound is not None else self.get_pagecount()

        return progress.Progress(
            self.get_progress_template(),
            rb,
            xrange(lb, rb+1)
        )


    def get_progress_template (self):
        return self.task_name + ' : {dynamic} [{frac:.1%}] {fixedline}'



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
        results = deque()
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
        self.pool = Pool(64)


    def start_parse_linkpage (self, page):
        #results  = deque()
        #handlers = wcp.Pool(self.get_content_handler(results))
        #for el in self.get_elements(page):
        #    handlers.add(el)
        #handlers.process()

        #return results
        return self.pool.map(self.get_content_handler(), self.get_elements(page))



    def get_content_handler (self):
        def method (url):
            try:
                content = self.get_page_content(url)
                if content is None:
                    raise Exception
                else:
                    return self.get_page_data(
                        url,
                        parser(content).cssselect(self.css_content)[0]
                    )
            except Exception as e:
                stderr.write('**^ Problems with {0}. Please check.\n'.format(url))

        return method


    def get_elements (self, document):
        return imap(
            lambda el: self.construct_url(el),
            ( el.get('href') for el in document.cssselect(self.css_elements) )
        )


    def get_sorter (self, tupl):
        return tupl[1] + tupl[2]
