#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       __init__.py
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



import random



__all__ = (
    'p4reviews',
    'disreviews',
    'p4news',
    'disnews',
    'gorillavsbear',
    'quietusnews',
    'quietusreviews',
    'factnews',
    'factreviews',
    'dustedreviews',
    'lookatme',
    'afishareviews'
)

_plugins = {} # {plugin_name : plugin_class}



def register (plugin_class, *plugin_names):
    for name in plugin_names:
        if name in _plugins:
            raise KeyError(name)

    for name in plugin_names:
        _plugins[name] = plugin_class


def unregister(*plugin_names):
    for name in plugin_names:
        try:
            del _plugin[name]
        except KeyError:
            pass


def have_plugin (plugin_name):
    return plugin_name in _plugins


def get_unknown_plugins (plugin_names):
    return filter(
        lambda name: not have_plugin(name),
        plugin_names
    )


def going_for_all (plugin_names):
    return len(plugin_names) == 1 and 'all' == plugin_names[0]


def prepared (plugs):
    ret = list(frozenset(plugs))
    random.shuffle(ret) # trick to decrease load on particular service
    return ret


def get_registered_plugins (plugin_names):
    return ( _plugins[name] for name in plugin_names )


def get_plugins (plugin_names):
    if going_for_all (plugin_names):
        return prepared(_plugins.values())
    else:
        unknown = get_unknown_plugins(plugin_names)
        if len(unknown) == 0:
            return prepared(get_registered_plugins(plugin_names))
        else:
            raise ValueError('Unknown plugins: {0}'.format(str(unknown)))
