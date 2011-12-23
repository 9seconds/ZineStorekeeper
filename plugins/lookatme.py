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



import datetime

from utils.website   import OneStep, parser
from utils.papercuts import convert_date, stripped, exceptionable, urlopen


MONTHS = {
    u'января'   : u'january',
    u'февраля'  : u'february',
    u'марта'    : u'march',
    u'апреля'   : u'april',
    u'мая'      : u'may',
    u'июня'     : u'june',
    u'июля'     : u'july',
    u'августа'  : u'august',
    u'сентября' : u'september',
    u'октября'  : u'october',
    u'ноября'   : u'november',
    u'декабря'  : u'december'
}
YEAR = str(datetime.datetime.today().year)



class LookAtMe (OneStep):


    @staticmethod
    @stripped
    @exceptionable
    def get_title (el):
        return el.cssselect('header .title a')[0].text_content()


    @staticmethod
    @stripped
    @exceptionable
    def get_author (el):
        return el.cssselect('.data a.author')[0].text_content()


    @staticmethod
    @exceptionable
    def get_date (el):
        date = el.cssselect('.data span')[0].text_content().replace(u'года', '').strip().split(u' ')

        if len(date) == 2: # 20 октября, без указания года = текущий год
            date.append(YEAR)
        date[1] = MONTHS[date[1]]

        return convert_date(u' '.join(date))


    @exceptionable
    def get_url (self, el):
        return self.construct_url(
            el.cssselect('header .title a')[0].get('href')
        )


    def __init__ (self, output = None):
        csv_header = ('URL', 'Title', 'Author', 'Date')
        super(LookAtMe, self).__init__(
            'lookatme.ru',
            '/flow/posts/music-radar?page={0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name = self.domain


    def get_pagecount (self):
        handler    = urlopen(self.page_counter.construct_url(1))
        pagination = parser(handler.read()).cssselect('section.paginator li.list-item a')
        handler.close()
        return int(pagination[-1].text)


    def get_elements (self, page):
        return page.cssselect('article.g-item-flow .caption')


    def handle_element(self, element):
        url    = self.get_url(element)
        title  = self.get_title(element)
        author = self.get_author(element)
        date   = self.get_date(element)

        return (url, title, author, date)



LookAtMe.register()
