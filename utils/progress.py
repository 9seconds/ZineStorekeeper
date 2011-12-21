#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       progress.py
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



from sys import stdout



class Progress:


    @staticmethod
    def get_charcount (frac, max_charcount):
        return int(round( frac*max_charcount ))


    def __init__ (self, template, unitcount, iterable, char = '=', max_charcount = 80):
        self.template      = template
        self.unitcount     = unitcount
        self.iterable      = iter(iterable)
        self.max_charcount = max_charcount
        self.char          = char
        self.current       = 0
        self.dynamic       = ''


    def set_dynamic (self, dynamic_content):
        self.dynamic = dynamic_content
        self.show()


    def __iter__ (self):
        return self


    def next (self):
        try:
            self.unit = self.iterable.next()
        except StopIteration as e:
            stdout.write("\n")
            raise StopIteration

        self.current += 1
        self.show()

        return self.unit


    def show (self):
        stdout.write('\r' + self.get_progressbar(
            self.get_runline(),
            self.get_fixedline()
        ))
        stdout.flush()


    def get_line (self, runline):
        without_line = self.get_progressbar('', '') \
            if runline \
            else self.get_progressbar(self.get_runline(), '')

        if len(without_line) >= self.max_charcount:
            return ''
        else:
            line_length = self.get_charcount(
                self.get_frac(),
                self.max_charcount - len(without_line)
            )
            chars = line_length*self.char
            return chars \
                if runline \
                else chars + ' '*(
                    self.max_charcount - len(without_line) - line_length
                )


    def get_runline (self):
        return self.get_line(True)


    def get_fixedline (self):
        return self.get_line(False)


    def get_frac (self):
        return float(self.current) / self.unitcount


    def get_percentage (self):
        return 100.0 * self.get_frac()


    def get_progressbar (self, runline, fixedline):
        return self.template.format(
            frac        = self.get_frac(),
            percent     = self.get_percentage(),
            currentunit = self.unit,
            currentiter = self.current,
            totaliter   = self.unitcount,
            dynamic     = self.dynamic,
            runline     = runline,
            fixedline   = fixedline
        )
