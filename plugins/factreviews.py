#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       factreviews.py
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



from decimal         import Decimal

from utils.website   import TwoStep
from utils.papercuts import convert_date, stripped



class FactReviews (TwoStep):


    @staticmethod
    def get_aa_line (info):
        album = info.cssselect('.category-reviews h9 i')[0].text_content().strip()
        whole_line = info.cssselect('.category-reviews h9')[0].text_content()
        artist = whole_line.replace(album, '').strip()

        return (artist[:-1], album)


    @staticmethod
    @stripped
    def get_artist (info):
        return FactReviews.get_aa_line(info)[0]


    @staticmethod
    @stripped
    def get_album (info):
        return FactReviews.get_aa_line(info)[1]


    @staticmethod
    @stripped
    def get_label (info):
        ret = info.findall('p')[1].text_content().replace('Available on:', '').split()
        return ' '.join(ret[:-1])


    @staticmethod
    def get_date (info):
        return convert_date(
            info.cssselect('#greyBox')[0].text_content().split(',')[1].split('and')[0]
        )


    @staticmethod
    @stripped
    def get_author (info):
        return info.findall('p')[-2].text_content()


    @staticmethod
    def get_score (info):
        have = lambda pattern: len(
            info.cssselect( FactReviews.get_score_css(pattern) )
        ) > 0

        idx = Decimal(0)
        inc = Decimal(0.5)
        for i in xrange(10):
            idx += inc
            if have(idx):
                return float(idx)
        else:
            return 0


    @staticmethod
    def get_score_css (number):
        css = str(number).replace('.', '')
        return 'table.record%s-article' % (css if not css.endswith('0') else css[:-1])


    def __init__ (self, output = None):
        csv_header = ('URL', 'Artist', 'Album', 'Label', 'Date', 'Score')
        super(FactReviews, self).__init__(
            'factmag.com',
            '/category/reviews/page/{0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name    = '{0} reviews'.format(self.domain)
        self.css_elements = '.content a.archiveTitle'
        self.css_content  = '.home'


    def get_page_data (self, url, content):
        artist = self.get_artist(content)
        album  = self.get_album(content)
        label  = self.get_label(content)
        date   = self.get_date(content)
        author = self.get_author(content)
        score  = self.get_score(content)

        return (url, artist, album, label, date, author, score)


    def get_elements (self, document):
        return ( el.get('href') for el in document.cssselect(self.css_elements) )



FactReviews.register()
