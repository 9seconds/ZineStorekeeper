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


import itertools

import website


class P4Reviews (website.Site):

    def __init__ (self, output = None):
        csv_header = ('Artist', 'Album', 'Label', 'Year', 'Author', 'Score', 'Url')
        super(P4Reviews, self).__init__('pitchfork.com', '/reviews/albums/{0}', output = output, csv_header = csv_header)

    @staticmethod
    @website.stripped
    def get_artist (info):
        return info.find('h1').find('a').text if len(info.find('h1')) > 0 else info.find('h1').text

    @staticmethod
    @website.stripped
    def get_album (info):
        return info.find('h2').text

    @staticmethod
    @website.stripped
    def get_label (info):
        return info.find('h3').text.split(';')[0]

    @staticmethod
    @website.stripped
    def get_year (info):
        return info.find('h3').text.split(';')[1]

    @staticmethod
    @website.stripped
    def get_author (info):
        return info.find('div')[0].text.replace('By', '').split(';')[0]

    @staticmethod
    @website.stripped
    def get_score (info):
        return info.findall('div')[1].findall('span')[0].text

    def get_content_handler (self, results):
        @website.ContentHandler.Method
        def method (url):
            page = self.get_page_content(url)

            doc = website.parser.document_fromstring(page)
            info = doc.cssselect('.review-tombstone .review-info')[0]

            artist = self.get_artist(info)
            album = self.get_album(info)
            label = self.get_label(info)
            year = self.get_year(info)
            author = self.get_author(info)
            score = self.get_score(info)

            method.say(str((artist, album, label, year, author, score)))
            results.append((artist, album, label, year, author, score, url))
        return method

    def get_elements (self, document):
        els = (el.get('href') for el in document.cssselect('.review-item .review a'))
        return itertools.imap(lambda el: self.construct_url(el), els)
