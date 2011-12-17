#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       disnews.py
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



import website
import utils



class DISNews (website.TwoStep):


    @staticmethod
    @website.stripped
    def get_title (info):
        return info.cssselect('h1.title')[0].text_content()


    @staticmethod
    @website.stripped
    def get_author (info):
        return info.cssselect('.content .byline .b_author a.author')[0].text


    @staticmethod
    def get_date (info):
        return utils.convert_date(
            info.cssselect('.content .byline .date')[0].text
        )


    def __init__ (self, output = None):
        csv_header = ('URL', 'Title', 'Author', 'Date')
        super(DISNews, self).__init__(
            'drownedinsound.com',
            '/news/page/{0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name    = '{0} news'.format(self.domain)
        self.css_elements = '#content .post .inner h4 a'
        self.css_content  = '#content'


    def get_page_data (self, url, content):
        title  = self.get_title(content)
        author = self.get_author(content)
        date   = self.get_date(content)

        return (url, title, author, date)


    def get_pagecount (self):
        handler    = utils.urlopen(self.page_counter.construct_url(1))
        pagination = website.parser(handler.read()).cssselect('#content .pagination a')
        handler.close()
        return int(pagination[-2].text)



DISNews.register()
