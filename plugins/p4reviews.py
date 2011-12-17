#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       p4reviews.py
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



from utils.website   import TwoStep
from utils.papercuts import convert_date, stripped



class P4Reviews (TwoStep):


    @staticmethod
    @stripped
    def get_artist (info):
        return info.find('h1').find('a').text \
            if len(info.find('h1')) > 0 \
            else info.find('h1').text


    @staticmethod
    @stripped
    def get_album (info):
        return info.find('h2').text


    @staticmethod
    @stripped
    def get_label (info):
        return info.find('h3').text.split(';')[0]


    @staticmethod
    @stripped
    def get_year (info):
        year = info.find('h3').text.split(';')[1]
        return year.split('/')[1] if '/' in year else year


    @staticmethod
    @stripped
    def get_author (info):
        return info.find('div')[0].text.replace('By', '').split(';')[0]


    @staticmethod
    def get_date (info):
        return convert_date(info.find('div')[0].text.split(';')[1])


    @staticmethod
    def get_score (info):
        return float(info.findall('div')[1].findall('span')[0].text.strip())


    def __init__ (self, output = None):
        csv_header = ('URL', 'Artist', 'Album', 'Label', 'Year', 'Publication date', 'Author', 'Score')
        super(P4Reviews, self).__init__(
            'pitchfork.com',
            '/reviews/albums/{0}',
            output     = output,
            csv_header = csv_header
        )
        self.task_name    = '{0} reviews'.format(self.domain)
        self.css_elements = '.review-item .review a'
        self.css_content  = '.review-tombstone .review-info'


    def get_page_data (self, url, content):
        artist = self.get_artist(content)
        album  = self.get_album(content)
        label  = self.get_label(content)
        year   = self.get_year(content)
        author = self.get_author(content)
        date   = self.get_date(content)
        score  = self.get_score(content)

        return (url, artist, album, label, year, date, author, score)


    def get_sorter (self, tupl):
        return tupl[1] + tupl[2]



P4Reviews.register()
