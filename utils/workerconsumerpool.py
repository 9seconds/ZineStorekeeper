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



import multiprocessing

from Queue     import Queue, Empty as EmptyError
from sys       import stderr
from time      import sleep
from threading import Thread, Event as ThreadEvent


CPU_COUNT    = multiprocessing.cpu_count()
WORKER_COUNT = 6*CPU_COUNT


class Worker (Thread):


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

        @staticmethod
        def panic (message):
            stderr.write(str(message) + "\n")

        def __init__ (self, function):
            super(self.__class__, self).__init__(function)

            self._function.say   = self.say
            self._function.panic = self.panic


    _timeout = 0.001


    def __init__ (self, queue, method):
        self.queue  = queue
        self.method = method
        self._stop  = ThreadEvent()

        super(Worker, self).__init__()
        self.daemon = True

    def run (self):
        while not self._stop.is_set():
            try:
                self.method(self.queue.get(timeout=self._timeout))
                self.queue.task_done()
            except EmptyError:
                pass

    def stop (self):
        self._stop.set()



class Pool:


    @staticmethod
    def _alert (message):
        print str(message)


    def __init__ (
        self,
        worker_method,
        worker_count = WORKER_COUNT
    ):
        self.worker_count    = worker_count
        self.worker_method   = worker_method
        self.queue           = Queue()
        self.messages        = Queue()

        sleep(.1) # dirty hack because Queue is not set stable

        self.worker_method.say = lambda message : self.messages.put(message)


    def process (self):
        workers = self._create_workers()
        herald  = self._create_herald()

        self._waiting()

        workers.append(herald)
        self._disband(workers)


    def add (self, task):
        self.queue.put(task)
        return self


    def _create_workers (self):
        workers = []

        for i in xrange(self.worker_count):
            worker = Worker(self.queue, self.worker_method)
            workers.append(worker)
            worker.start()

        return workers


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
