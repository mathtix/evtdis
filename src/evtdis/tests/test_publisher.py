"""
Copyright 2018 - MathTix, LLC - All rights reserved.
"""

import logging.config
from os import path
from unittest import TestCase
from evtdis import Publisher
from evtdis import EventType

# Setup logging
log_file = path.join(path.dirname(path.abspath(__file__)), 'testlog.conf')
logging.config.fileConfig(fname=log_file, disable_existing_loggers=False)
_LOGGER = logging.getLogger(__name__)


class TestPublisher(TestCase):

    One: type = EventType(name='One', p1=int)
    Two: type = EventType(name='Two', p2=str, p3=(tuple, (1, 2, 3)))

    def __init__(self, methodName='runTest'):
        TestCase.__init__(self, methodName=methodName)
        self.publisher: Publisher = None
        self.argsOne: tuple = None
        self.argsTwo: tuple = None

    def setUp(self):
        self.argsOne = None
        self.argsTwo = None
        self.publisher = Publisher(name='Test')
        self.publisher.registerEvent(eventType=TestPublisher.One)
        self.publisher.registerEvent(eventType=TestPublisher.Two)

    def subscribe(self):
        self.publisher.subscribe(eventType=TestPublisher.One, call=self.eventOneCB)
        self.publisher.subscribe(eventType=TestPublisher.Two, call=self.eventTwoCB)

    def tearDown(self):
        del self.publisher
        self.publisher = None
        self.argsOne = None
        self.argsTwo = None

    def eventOneCB(self, p1: int):
        self.argsOne = (p1, )

    def eventTwoCB(self, p2: str, p3: tuple):
        self.argsTwo = p2, p3

    def test_register_unregister(self):
        self.subscribe()

        self.publisher.unregisterEvent(eventType=TestPublisher.One)
        self.assertTrue(TestPublisher.One not in self.publisher.eventTypes)
        self.assertTrue(TestPublisher.Two in self.publisher.eventTypes)

        self.publisher.unregisterEvent(eventType=TestPublisher.Two)
        self.assertTrue(TestPublisher.Two not in self.publisher.eventTypes)

    def test_subscribe_unsubscribe(self):
        self.publisher.subscribe(eventType=TestPublisher.One, call=self.eventOneCB)
        self.publisher.subscribe(eventType=TestPublisher.Two, call=self.eventTwoCB)

        self.assertTrue(self.eventOneCB in self.publisher.subscribers(eventType=TestPublisher.One))
        self.assertTrue(self.eventTwoCB in self.publisher.subscribers(eventType=TestPublisher.Two))

        self.publisher.unsubscribe(eventType=TestPublisher.One, call=self.eventOneCB)
        self.assertTrue(self.eventOneCB not in self.publisher.subscribers(eventType=TestPublisher.One))

        self.publisher.unsubscribe(eventType=TestPublisher.Two, call=self.eventTwoCB)
        self.assertTrue(self.eventTwoCB not in self.publisher.subscribers(eventType=TestPublisher.Two))

    def test_publish(self):
        self.subscribe()

        p1 = 5
        self.publisher.publish(self.One(p1=p1))
        self.assertEqual(self.argsOne, (p1, ))

        p2 = 'The Doctor'
        p3 = 1, 2, 'three'
        self.publisher.publish(self.Two(p2=p2, p3=p3))
        self.assertEqual(self.argsTwo, (p2, p3))
