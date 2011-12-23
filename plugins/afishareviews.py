#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       afishareviews.py
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
from utils.papercuts import convert_rudate, stripped, exceptionable, urlopen



class AfishaReviews (TwoStep):


    @staticmethod
    @exceptionable
    def get_ly_line (info):
        return info.cssselect('.b-object-summary .m-margin-btm')[0].text_content()\
            .strip().split("\n")[-1].split(',')


    @staticmethod
    @stripped
    @exceptionable
    def get_artist (info):
        return info.cssselect('.b-object-summary .b-object-header h1')[0].text_content()


    @staticmethod
    @stripped
    @exceptionable
    def get_album (info):
        return info.cssselect('.b-object-summary a')[0].text_content()\
            .replace(u'«', '').replace(u'»', '')


    @staticmethod
    @stripped
    @exceptionable
    def get_label (info):
        return AfishaReviews.get_ly_line(info)[0]


    @staticmethod
    @stripped
    @exceptionable
    def get_release_year (info):
        return AfishaReviews.get_ly_line(info)[1]


    @staticmethod
    @exceptionable
    def get_pubdate (info):
        return convert_rudate(
            info.cssselect('.b-review-list .b-entry-info')[0].text_content()\
                .strip().split("\n")[0].strip()
        )


    @staticmethod
    @stripped
    @exceptionable
    def get_author (info):
        return info.cssselect('.b-review-list .user h3 a')[0].text_content()


    @staticmethod
    @exceptionable
    def get_score (info):
        line = info.cssselect('.b-review-list .b-rating em.mask')[0].get('title')
        return int(line[8:-5]) if u':' in line else 0


    def __init__ (self, output = None):
        csv_header = ('URL', 'Artist', 'Album', 'Label', 'Release Year', 'Publication date', 'Author', 'Score')
        super(AfishaReviews, self).__init__(
            'afisha.ru',
            '/cd/cd_list/page{0}/sortbyalpha/',
            output     = output,
            csv_header = csv_header
        )
        self.task_name    = '{0} reviews'.format(self.domain)
        self.css_content  = '#content'


    def get_page_data (self, url, content):
        artist       = self.get_artist(content)
        album        = self.get_album(content)
        label        = self.get_label(content)
        release_year = self.get_release_year(content)
        pub_date     = self.get_pubdate(content)
        author       = self.get_author(content)
        score        = self.get_score(content)

        return (url, artist, album, label, release_year, pub_date, author, score)


    def get_elements (self, document):
        for el in document.cssselect('#objects-list .places-list-item'):
            if len(el.cssselect('a')) > 1: # как правило, если там есть 2 ссылки (альбом и лейбл), то рецензия не битая
                yield el.cssselect('h3 a')[0].get('href')


    def get_pagecount (self):
        handler    = urlopen(self.page_counter.construct_url(1))
        pagination = parser(handler.read()).cssselect('#ctl00_CenterPlaceHolder_ucPager_LastPageLink')[0]
        handler.close()
        return int(pagination.text)



AfishaReviews.register()
