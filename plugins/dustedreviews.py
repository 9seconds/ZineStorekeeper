#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       dustedreviews.py
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



import string

from utils.website   import TwoStep
from utils.papercuts import convert_date, stripped, exceptionable



class DustedReviews (TwoStep):


    @staticmethod
    def handle_topblock (info, element_number):
        return ':'.join(info[element_number].text_content().split(':')[1:])


    @staticmethod
    @stripped
    @exceptionable
    def get_artist (info):
        return DustedReviews.handle_topblock(info, 0)


    @staticmethod
    @stripped
    @exceptionable
    def get_album (info):
        return DustedReviews.handle_topblock(info, 1)


    @staticmethod
    @stripped
    @exceptionable
    def get_label (info):
        return DustedReviews.handle_topblock(info, 2)


    @staticmethod
    @exceptionable
    def get_date (info):
        return convert_date(DustedReviews.handle_topblock(info, 3))


    @staticmethod
    @stripped
    @exceptionable
    def get_author (info):
        return info[-1].text_content().split('\n')[0].replace('By', '')


    def __init__ (self, output = None):
        csv_header = ('URL', 'Artist', 'Album', 'Label', 'Author', 'Date')
        super(DustedReviews, self).__init__(
            'dustedmagazine.com',
            '/reviews/archive/{0}',
            output     = output,
            csv_header = csv_header,
            encoding   = 'iso-8859-1'
        )
        self.task_name   = '{0} reviews'.format(self.domain)
        self.str_range   = '0' + string.ascii_lowercase
        self.css_content = 'body'

        self.xpath_content  = '/html/body/table[3]/tr[2]/td[3]/'
        self.xpath_elements = self.xpath_content + 'p[@class="center"]/a'
        self.xpath_topblock = self.xpath_content + 'table/tr/td/table/tr/td/table/tr/td/p[@class="close"]'
        self.xpath_review   = self.xpath_content + 'p'


    def get_progress (self, left_bound = None, right_bound = None):
        return self.str_range


    def get_pagecount (self):
        return len(self.str_range)


    def get_elements (self, page):
        return (
            el.get('href') \
            for el in page.xpath(self.xpath_elements)
        )


    def get_page_data (self, url, content):
        top_block    = content[0].xpath(self.xpath_topblock)
        review_block = content[0].xpath(self.xpath_review)

        artist = self.get_artist(top_block)
        album  = self.get_album(top_block)
        label  = self.get_label(top_block)
        date   = self.get_date(top_block)
        author = self.get_author(review_block)

        return (url, artist, album, label, author, date)



DustedReviews.register()
