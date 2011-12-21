#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       disreviews.py
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



from utils.website   import TwoStep, parser
from utils.papercuts import convert_date, stripped, exceptionable, urlopen



class DISReviews (TwoStep):


    @staticmethod
    @stripped
    @exceptionable
    def get_artist (info):
        return info.cssselect('.hreview .release_header .release_title h1 a')[0].text


    @staticmethod
    @stripped
    @exceptionable
    def get_album (info):
        return info.cssselect('.hreview .release_header .release_title h1 a')[1].text


    @staticmethod
    @stripped
    @exceptionable
    def get_label (info):
        return info.cssselect('.hreview .label_tokens .token a b')[0].text


    @staticmethod
    @exceptionable
    def get_releasedate (info):
        return convert_date(
            info.cssselect('.hreview .release_header .release_details')[0].text_content()\
                .strip().split()[-1]
        )

    @staticmethod
    @stripped
    @exceptionable
    def get_author (info):
        return info.cssselect('.hreview .b_author .author')[0].text


    @staticmethod
    @exceptionable
    def get_pubdate (info):
        return convert_date(
            info.cssselect('.hreview .byline .date')[0].text
        )


    @staticmethod
    @exceptionable
    def get_score (info):
        el = info.cssselect('.ratings .mark .value')
        return int(el[0].text.strip()) \
            if len(el) \
            else ''


    def __init__ (self, output = None):
        csv_header = ('URL', 'Artist', 'Album', 'Label', 'Release date', 'Publication date', 'Author', 'Score')
        super(DISReviews, self).__init__(
            'drownedinsound.com',
            '/releases/reviewed?page={0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name    = '{0} reviews'.format(self.domain)
        self.css_elements = '.content .review .inner h4 a'
        self.css_content  = '#content'


    def get_page_data (self, url, content):
        artist       = self.get_artist(content)
        album        = self.get_album(content)
        label        = self.get_label(content)
        release_date = self.get_releasedate(content)
        author       = self.get_author(content)
        pub_date     = self.get_pubdate(content)
        score        = self.get_score(content)

        return (url, artist, album, label, release_date, pub_date, author, score)


    def get_pagecount (self):
        handler    = urlopen(self.page_counter.construct_url(1))
        pagination = parser(handler.read()).cssselect('#content .pagination a')
        handler.close()
        return int(pagination[-2].text)


    def get_sorter (self, tupl):
        return tupl[1] + tupl[2]



DISReviews.register()
