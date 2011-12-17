#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       pagecounter.py
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



import math

from .papercuts import urlopen, HTTP404



class PageCounter:


    def __init__ (self, url_template, left_bound = 1, naive_bound = 5):
        self.url_template = url_template
        self.left_bound   = left_bound
        self.naive_bound  = naive_bound
        self.page_count   = None


    def get_max_pagenumber (self):
        if self.page_count is None:
            for page_number in xrange(*self.get_naive_range()):
                if not self.is_page_available(page_number):
                    self.page_count = page_number-1
                    break

        return self.page_count


    def get_initial_right_bound (self):
        right_bound = self.left_bound + 2
        tries       = 0

        coef = lambda x : self.naive_bound * int( math.ceil(math.log1p(x)) )

        while self.is_page_available(right_bound):
            tries       += 1
            right_bound  = 1 + coef(tries)*right_bound

        return right_bound


    def get_naive_range (self):
        left_bound  = self.left_bound
        right_bound = self.get_initial_right_bound()

        while (right_bound - left_bound) > self.naive_bound:
            page_number = left_bound + (right_bound - left_bound) // 2
            if self.is_page_available(page_number):
                left_bound = page_number
            else:
                right_bound = page_number

        return (left_bound, right_bound+1)


    def is_page_available (self, token):
        try:
            urlopen(self.construct_url(token)).close()
            return True
        except HTTP404:
            return False


    def construct_url (self, page_number):
        return self.url_template.format(page_number)
