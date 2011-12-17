#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       quietusnews.py
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



from utils.website   import TwoStep, parser, parser_str
from utils.papercuts import convert_date, stripped, urlopen



class QuietusNews (TwoStep):


    @staticmethod
    def get_subline_content (info):
        parts = info.cssselect('h2 .sub_sub')[0].text_content().strip().split()
        return (
            ' '.join(parts[:-5]),
            ' '.join(parts[-4:])
        )


    @staticmethod
    @stripped
    def get_title (info):
        return parser_str(info.find('h2')).split('<br>')[0].split('<h2>')[1]


    @staticmethod
    @stripped
    def get_author (info):
        return QuietusNews.get_subline_content(info)[0]


    @staticmethod
    def get_date (info):
        return convert_date(
            QuietusNews.get_subline_content(info)[1]
        )


    def __init__ (self, output = None):
        #csv_header = ('URL', 'Title', 'Author', 'Date')
        csv_header = ('URL', 'Title', 'Date')
        super(QuietusNews, self).__init__(
            'thequietus.com',
            '/news/page/{0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name    = '{0} news'.format(self.domain)
        self.css_elements = '#content div.holder li.holder h4 a'
        self.css_content  = '#content .section .section_header'


    def get_page_data (self, url, content):
        title  = self.get_title(content)
        #author = self.get_author(content)
        date   = self.get_date(content)

        #return (url, title, author, date)
        return (url, title, date)


    def get_pagecount (self):
        handler    = urlopen(self.page_counter.construct_url(1))
        pagination = parser(handler.read()).cssselect('#content .pagination a')
        handler.close()
        return int(pagination[-2].text)



QuietusNews.register()
