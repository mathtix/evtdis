"""
Copyright 2018 - MathTix, LLC - All rights reserved.
"""

import logging.config
import sys
from os import path
from queue import PriorityQueue
from unittest import TestCase
from evtdis import EventType
from evtdis import Event

log_file = path.join(path.dirname(path.abspath(__file__)), 'testlog.conf')
logging.config.fileConfig(fname=log_file, disable_existing_loggers=False)
_LOGGER = logging.getLogger(__name__)


class TestEvent(TestCase):

    def __init__(self, methodName='runTest'):
        TestCase.__init__(self, methodName=methodName)

    def func(self, p1: int, p2: str) -> dict:
        _LOGGER.info('func called: p1 = %s  p2 = %s', p1, p2)
        return {'p1': p1, 'p2': p2}

    def test_event_dispatch(self):
        DispatchEvent = EventType(name='DispatchEvent', priority=5, p1=int, p2=(str, 'trash'))
        event: DispatchEvent = DispatchEvent(p1=90, p2='Hello')
        ret: dict = self.func(**event)
        self.assertEqual(dict(event), ret)

    def test_event_priority_queue(self):
        # Define the events types.
        EventZero = EventType(name='EventZero', priority=1, p1=int, p2=(str, 'trash'))
        EventOne = EventType(name='EventOne', priority=5, p1=int, p2=(str, 'hash'))
        EventTwo = EventType(name='EventTwo', priority=7, p1=int, p2=(str, 'mash'))
        EventThree = EventType(name='EventThree', priority=0)
        EventFour = EventType(name='EventFour', priority=0, p1=float, p2=list, p3=bool)

        # Put events in a queue.
        q = PriorityQueue(maxsize=16)
        q.put(item=EventOne(p1=1, p2='trouble'))
        q.put(item=EventTwo(p1=0))
        q.put(item=EventOne(p1=2))
        q.put(item=EventOne(p1=2, p2='goodbye'))
        q.put(item=EventThree())
        q.put(item=EventFour(p1=4.0, p2=[1, 2, 3], p3=True))

        # Verify the deque order follows priority
        last = -(sys.maxsize - 1)
        for idx in range(0, q.qsize()):
            evt: Event = q.get(block=False)
            _LOGGER.info('evt.priority = %s  last = %s', evt.priority, last)
            self.assertTrue(evt.priority >= last)
            last = evt.priority
            _LOGGER.info('priority = %s %s %s', evt.priority, evt.__class__.__qualname__, evt)

    def test_incorrect_parameter_usage(self):
        BadEvent = EventType(name='BadEvent', priority=5, p1=int, p2=(str, 'trash'))
        with self.assertRaises(TypeError):
            # Pass an integer instead of a string for parameter two.
            BadEvent(p1=90, p2=6)
        with self.assertRaises(RuntimeError):
            BadEvent(p1=90, someRandomArgument=6)
        with self.assertRaises(RuntimeError):
            BadEvent()
