#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       main.py
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



import sys
import gc


def err (module_name, package_name):
    sys.stderr.write(
        "{0} module is unavaliable. Please install it\n(e.g. 'sudo apt-get install {1}')\n".format(
            module_name,
            package_name
    ))
    sys.exit(2)


try:
    import lxml
except ImportError:
    err('lxml', 'python-lxml')

try:
    import dateutil
except ImportError:
    err('dateutil', 'python-dateutil')

try:
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all()
except ImportError:
    err('gevent', 'python-gevent')



from plugins import *
import plugins



try:
    for site in plugins.get_plugins(sys.argv[1:]):
        task = site()
        print 'Handling {0}'.format(task.task_name)
        gc.collect()
        task.handle()
except ValueError as e:
    print e
    print 'You shoud run program with "all" key or with a subset of following keys:'
    for name in sorted(plugins.__all__):
        print '  - ' + name
