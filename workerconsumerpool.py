#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       workerconsumerpool.py
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



import threading
import multiprocessing
import collections
import time
import gc

from Queue import Queue
from Queue import Empty as EmptyError




class Worker (threading.Thread):



    class Function (object):

        @staticmethod
        def appropriate_function (function):
            try:
                return callable(function) and function.func_code.co_argcount == 1
            except AttributeError:
                return False

        def __init__ (self, function):
            if self.appropriate_function (function):
                self._function = function
            else:
                raise TypeError('Given argument is not appropriate Worker function')

        def __call__ (self, argument):
            return self._function(argument)



    class Method (Function):

        @staticmethod
        def say (message):
            print str(message)

        def __init__ (self, function):
            super(self.__class__, self).__init__(function)

            self._function.say = self.say



    class Callback (Function):

        def __init__ (self, function):
            super(self.__class__, self).__init__(function)

            if 'self' != function.func_code.co_varnames[0]:
                raise TypeError('Given function is not Callback applicable')

            self._function._callback = None

        @property
        def function (self):
            return self._function



    _timeout = 0.001

    @staticmethod
    @Callback
    def default_callback (self):
        pass

    def __init__ (self, queue, method):
        self.queue  = queue
        self.method = method
        self._callback = self.default_callback.function
        self._stop  = threading.Event()

        super(Worker, self).__init__()
        self.daemon = True

    def _set_callback (self, callback):
        if not isinstance (callback, Worker.Callback):
            raise TypeError('Given function is not Callback applicable')
        self._callback = callback.function

    def stop (self):
        self._stop.set()

    def run (self):
        while not self._stop.is_set():
            try:
                self.method(self.queue.get(timeout=self._timeout))
                self._callback(self)
                self.queue.task_done()
            except EmptyError:
                pass

    callback = property(None, _set_callback)



class Pool:

    def __init__ (
        self,
        worker_method,
        worker_callback = Worker.default_callback,
        worker_count    = 4*multiprocessing.cpu_count()
    ):
        self.worker_count    = worker_count
        self.worker_method   = worker_method
        self.worker_callback = worker_callback
        self.queue           = Queue()
        self.messages        = Queue()

        time.sleep(.1) # dirty hack because Queue is not set stable

        self.worker_method.say = lambda message : self.messages.put(message)

    def add (self, task):
        self.queue.put(task)
        return self

    def _create_workers (self):
        workers = collections.deque()

        for i in xrange(self.worker_count):
            worker = Worker(self.queue, self.worker_method)
            worker.callback = self.worker_callback
            workers.append(worker)
            worker.start()

        return workers

    @staticmethod
    def _alert (message):
        print str(message)

    def _create_herald (self):
        herald = Worker(self.messages, self._alert)
        herald.start()

        return herald

    def _waiting (self):
        self.queue.join()
        self.messages.join()

    def _disband (self, workers):
        for worker in workers:
            worker.stop()

    def process (self):
        workers = self._create_workers()
        herald  = self._create_herald()

        self._waiting()

        workers.append(herald)
        self._disband(workers)

        gc.collect()
