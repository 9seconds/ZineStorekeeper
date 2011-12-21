#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       quietusreviews.py
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



from itertools       import imap, chain

from utils.website   import TwoStep, parser, parser_str
from utils.papercuts import convert_date, stripped, exceptionable, urlopen



class QuietusReviews (TwoStep):


    @staticmethod
    @exceptionable
    def get_subline_content (info):
        parts = info.cssselect('h2 .sub_sub')[0].text_content().strip().split()
        return (
            ' '.join(parts[:-5]),
            ' '.join(parts[-4:])
        )


    @staticmethod
    @exceptionable
    def get_review_urls (document, css):
        return ( el.find('a').get('href') for el in document.cssselect(css) )


    @staticmethod
    @stripped
    @exceptionable
    def get_artist (info):
        return parser_str(info.find('h2')).split('<br>')[0].split('<h2>')[1]


    @staticmethod
    @stripped
    @exceptionable
    def get_album (info):
        return info.cssselect('h2 .sub')[0].text_content()


    @staticmethod
    @stripped
    @exceptionable
    def get_author (info):
        return QuietusReviews.get_subline_content(info)[0]


    @staticmethod
    @exceptionable
    def get_date (info):
        return convert_date(
            QuietusReviews.get_subline_content(info)[1]
        )


    def __init__ (self, output = None):
        csv_header = ('URL', 'Artist', 'Album', 'Author', 'Date')
        super(QuietusReviews, self).__init__(
            'thequietus.com',
            '/reviews?page={0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name    = '{0} reviews'.format(self.domain)
        self.css_content  = '#content .section .section_header'


    def get_page_data (self, url, content):
        artist = self.get_artist(content)
        album  = self.get_album(content)
        author = self.get_author(content)
        date   = self.get_date(content)

        return (url, artist, album, author, date)


    def get_pagecount (self):
        handler    = urlopen(self.page_counter.construct_url(1))
        pagination = parser(handler.read()).cssselect('#content .pagination a')
        handler.close()
        return int(pagination[-2].text)


    def get_elements (self, document):
        return imap(
            lambda el: self.construct_url(el),
            chain(
                self.get_review_urls(document, '#content .review'),
                self.get_review_urls(document, '#content .review_small')
            )
        )



QuietusReviews.register()
