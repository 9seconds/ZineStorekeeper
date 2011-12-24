#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       p4news.py
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



from utils.website   import OneStep
from utils.papercuts import convert_date, stripped, exceptionable



class P4News (OneStep):


    @staticmethod
    @exceptionable
    def get_titlelink (el):
        return el.cssselect('h3.title a')[0]


    @staticmethod
    @exceptionable
    def get_posted (el):
        content = el.cssselect('.posted-at')[0].text_content().strip().split()
        return (
            ' '.join(content[1:-7]),
            ' '.join(content[-6:])
        )


    @staticmethod
    @stripped
    @exceptionable
    def get_title (el):
        return P4News.get_titlelink(el).text_content()


    @staticmethod
    @stripped
    @exceptionable
    def get_author (el):
        return P4News.get_posted(el)[0]


    @staticmethod
    @exceptionable
    def get_date (el):
        return convert_date(P4News.get_posted(el)[1])


    def get_url (self, el):
        return self.construct_url(P4News.get_titlelink(el).get('href'))


    def __init__ (self, output = None):
        csv_header = ('URL', 'Artist', 'Album', 'Date')
        super(P4News, self).__init__(
            'pitchfork.com',
            '/news/{0}',
            output     = output,
            csv_header = csv_header,
            encoding   = 'utf-8'
        )
        self.task_name = '{0} news'.format(self.domain)


    def get_elements (self, page):
        return page.cssselect('#news-list .news-story')


    def handle_element(self, element):
        url    = self.get_url(element)
        title  = self.get_title(element)
        author = self.get_author(element)
        date   = self.get_date(element)

        return (url, title, author, date)



P4News.register()
