"""
Copyright 2018 - MathTix, LLC - All rights reserved.
"""

import logging
from inspect import ismethod
from threading import RLock
from typing import Any
from typing import Callable
from typing import List
from typing import Dict
from typing import Tuple
from .Event import Event

# Setup logging
_LOGGER = logging.getLogger(__name__)

EventCallback = Callable[..., Any]


class Publisher(object):
    """
    The Publisher class provides a thread safe mechanism for subclasses to register events
    which the publisher can deliver to subscribers and an interface that clients can use to
    subscribe for those published events. In a multi-threaded environment the targets can be
    invoked directly when there is no risk of the target calling back into the source of the
    event. If the commmunication is two way, all objects should have both a publisher for
    sending events and a dispatcher for receiving events.
    """

    def __init__(self, name='Instance') -> None:
        """
        Initialize a publisher with a specific name.
        :param name: The name of the publisher instance to be used in log messages.
        """
        # private
        self._name: str = name + ':Publisher'
        self._lock: RLock = RLock()
        self._subscribers: Dict[type, List[EventCallback]] = dict()

    def _log(self, msg, *args, **kwargs) -> None:
        msg: str = '[{}] '.format(self._name) + msg
        _LOGGER.debug(msg, *args, **kwargs)

    @property
    def eventTypes(self) -> Tuple[type, ...]:
        """
        Retrieve the events which the associated publisher instance generates.
        :return: A tuple of event event types which are subclasses of type.
        """
        with self._lock:
            eventTypes: tuple = tuple(self._subscribers.keys())
        return eventTypes

    def subscribers(self, eventType: type) -> Tuple[EventCallback]:
        """
        Retrieve the subscribers associated with the specified event.
        :param eventType: The event type for whose subscribers are to be queried
        :return: A tuple of callable objects which are the current targets of the specified event.
        """
        with self._lock:
            registered: bool = eventType in self._subscribers
            if registered:
                return tuple(self._subscribers[eventType])

        if not registered:
            raise Exception('Attempt to query unregistered event [{}]'.format(eventType))

    def registerEvent(self, eventType: type) -> None:
        """
        Register the specified event as published by this publisher.
        :param eventType: A subclass of type which identifies the event to be declared.
        """
        self._log('Declaring event %s', eventType)

        with self._lock:
            registered: bool = eventType in self._subscribers
            if not registered:
                # Add a list for subscribers
                self._subscribers[eventType] = list()

        if registered:
            raise Exception('Attempt to add registered event [{}]'.format(eventType))

    def unregisterEvent(self, eventType: type) -> None:
        """
        Remove the event from this publishers list of published events.
        :param eventType: A subclass of type which identifies the event to be undeclared.
        """

        self._log('Undeclaring event %s', eventType)

        with self._lock:
            registered: bool = eventType in self._subscribers
            if registered:
                # Remove the subscriber list.
                del self._subscribers[eventType]

        if not registered:
            raise Exception('Attempt to remove unregistered event [{}]'.format(eventType))

    def subscribe(self, eventType: type, call: EventCallback) -> None:
        """
        Subscribe the specified callable to the specified event.
        TO DO add filter parameter
        :param eventType: A subclass of type which identifies the event to which call should be subscribed.
        :param call: A callable object that is to be subscribed to the specified event.
        """
        self._log('Subscribe %s for event %s', call, eventType)

        if not callable(call):
            raise Exception('Callback parameter [{}] is not callable'.format(call))

        with self._lock:
            registered: bool = eventType in self._subscribers
            subscribed: bool = call in self._subscribers[eventType]
            if registered and not subscribed:
                self._subscribers[eventType].append(call)

        if not registered:
            raise Exception('Event type [{}] is not registered'.format(eventType))
        if subscribed:
            raise Exception('Call [{}] is already subscribed for event [{}]'.format(call, eventType))

    def unsubscribe(self, eventType: type, call: EventCallback) -> None:
        """
        Unsubscribe the specified call from the specified event.
        :param eventType: A subclass of type which identifies the event from which call should be unsubscribed.
        :param call: A callable object that is to be unsubscribed from the specified event.
        """
        self._log('Unsubscribe %s from event %s', call, eventType)

        if not callable(call):
            raise Exception('Callback parameter [{}] is not callable'.format(call))

        with self._lock:
            registered: bool = eventType in self._subscribers
            subscribed: bool = call in self._subscribers[eventType]
            if registered and subscribed:
                self._subscribers[eventType].remove(call)

        if not registered:
            raise Exception('Event type [{}] is not registered'.format(eventType))
        if not subscribed:
            raise Exception('Call [{}] is not subscribed for event [{}]'.format(call, eventType))

    def publish(self, event: Event) -> None:
        """
        Publish the input event and deliver it to all subscribers.
        :param event: An event subclass instance to be published.
        """
        self._log('Publishing event %s', event.__class__)

        with self._lock:
            registered: bool = type(event) in self._subscribers
            if registered:
                for subscriber in self._subscribers[type(event)]:
                    if ismethod(subscriber) and subscriber.__name__ == '_publishInternalEvent':
                        subscriber(event)
                    else:
                        subscriber(**event)

        if not registered:
            raise Exception('Attempt to trigger non-existent event [{}]'.format(id))
