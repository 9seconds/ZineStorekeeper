#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       factnews.py
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
from utils.papercuts import convert_date, stripped



class FactNews (OneStep):


    def get_url (self, el):
        return el.cssselect('a.archiveTitle')[0].get('href')


    @staticmethod
    @stripped
    def get_title (el):
        return el.cssselect('h2')[0].text_content()


    @staticmethod
    def get_date (el):
        return convert_date(
            el.cssselect('.postmetadata')[0].text_content().split('|')[0]
        )


    def __init__ (self, output = None):
        csv_header = ('URL', 'Title', 'Date')
        super(FactNews, self).__init__(
            'factmag.com',
            '/category/news/page/{0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name = '{0} news'.format(self.domain)


    def get_elements (self, page):
        return page.cssselect('.home .content .category-news')


    def handle_element(self, element):
        url    = self.get_url(element)
        title  = self.get_title(element)
        date   = self.get_date(element)

        return (url, title, date)



FactNews.register()
