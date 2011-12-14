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



import website
import utils



class P4News (website.OneStep):


    def get_url (self, el):
        return self.construct_url(
            el.find('h3').find('a').get('href')
        )


    @staticmethod
    @website.stripped
    def get_title (el):
        return el.find('h3').find('a').text


    @staticmethod
    @website.stripped
    def get_author (el):
        return el.find('div').text.split('on')[0].split('by ')[1]


    @staticmethod
    def get_pubdate (el):
        return utils.convert_date(el.find('div').text.split('on')[1].split('at')[0])


    def __init__ (self, output = None):
        csv_header = ('URL', 'Artist', 'Album', 'Label', 'Year', 'Publication date', 'Author', 'Score')
        super(P4News, self).__init__(
            'pitchfork.com',
            '/news/{0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name    = '{0} news'.format(self.domain)


    def get_elements (self, page):
        return page.cssselect('.news-story .content .story-title')


    def handle_element(self, element):
        url      = self.get_url(element)
        title    = self.get_title(element)
        author   = self.get_author(element)
        pub_date = self.get_pubdate(element)

        return (url, title, author, pub_date)


    def get_sorter (self, tupl):
        return tupl[0]
