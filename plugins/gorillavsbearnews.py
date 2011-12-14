#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       gorillavsbearnews.py
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



class GorillaVsBearNews (website.OneStep):


    def get_url (self, el):
        return el.cssselect('.postInfo h2 a')[0].get('href')


    @staticmethod
    @website.stripped
    def get_title (el):
        return el.cssselect('.postInfo .pagetitle')[0].text_content()


    @staticmethod
    @website.stripped
    def get_author (el):
        return el.cssselect(
            '.entry .postmetadataBottom'
        )[0].text_content().strip().split()[2]


    @staticmethod
    def get_date (el):
        return utils.convert_date(
            el.cssselect('.postInfo .pageTitleR')[0].text_content()
        )


    def __init__ (self, output = None):
        csv_header = ('URL', 'Title', 'Author', 'Date')
        super(GorillaVsBearNews, self).__init__(
            'gorillavsbear.net',
            '/page/{0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name = '{0} news'.format(self.domain)


    def get_elements (self, page):
        return page.cssselect('#content .post')


    def handle_element(self, element):
        url    = self.get_url(element)
        title  = self.get_title(element)
        author = self.get_author(element)
        date   = self.get_date(element)

        return (url, title, author, date)


    def get_sorter (self, tupl):
        return tupl[0]
