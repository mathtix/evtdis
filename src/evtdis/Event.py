"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import logging
from inspect import stack
from threading import Lock
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

_LOGGER = logging.getLogger(__name__)

ParameterDict = Dict[str, Union[type, Tuple[type, Any]]]


########################################################################################################################
# Event meta class to track the event parameters and default values.
########################################################################################################################

class EventMeta(type):
    """
    The EventMeta class tracks the parameters names and types, and default argument values of all events so
    that during construction of a specific event type these values are available to the event init method.
    """

    # Parameter definitions and default argument values for all events.
    _synchronize: Lock = Lock()
    _instances: Dict[str, ParameterDict] = {}

    ####################################################################################################################
    # Public class methods on Event
    ####################################################################################################################

    def getFullName(cls) -> str:
        """
        Retrieves the concatenation of the module name and qualified class name.
        :return: A string which contains the module and qualified class names.
        """
        return '{}.{}'.format(cls.__module__, cls.__qualname__)

    def getParameters(cls) -> ParameterDict:
        """
        Retrieves the event parameters for the associated event type.
        :return: A dictionary containing the event parameters.
        """
        with EventMeta._synchronize:
            parameters: ParameterDict = EventMeta._instances[EventMeta.getFullName(cls)]
        return parameters

    ####################################################################################################################
    # Private class methods on Event
    ####################################################################################################################

    def _setParameters(cls, parameters: ParameterDict) -> None:
        """
        Sets the parameters for the specified event type.
        :param parameters: A dictionary containing the parameter names, type, and optional default argument value.
        """
        name: str = EventMeta.getFullName(cls)
        with EventMeta._synchronize:
            if name in EventMeta._instances:
                raise TypeError('Event type [{}] already exists'.format(name))
            EventMeta._instances[EventMeta.getFullName(cls)] = parameters

    ####################################################################################################################
    # Internal
    ####################################################################################################################

    def __call__(mcs, *args, **kwargs):
        """
        Passes the parameter names, types, and default values to the event init method.
        :param args: ignored
        :param kwargs: A dictionary with keyword arguments from the event construction.
        :return: The initialized event instance.
        """
        return type.__call__(mcs, parameters=EventMeta.getParameters(mcs), arguments=kwargs)


########################################################################################################################
# Event subclass
########################################################################################################################

class Event(dict, metaclass=EventMeta):
    """
    Base class for event instances which
    """

    priority: int

    ####################################################################################################################
    # Overloaded operators for sorting in priority queues.
    ####################################################################################################################
    # Note this creates a problem as an instance has to be converted to a dictionary to compare values.

    def __eq__(self, other) -> bool:
        return self.priority == other.priority

    def __lt__(self, other) -> bool:
        return self.priority < other.priority

    def __gt__(self, other) -> bool:
        return self.priority > other.priority

    def __le__(self, other) -> bool:
        return self.priority <= other.priority

    def __ge__(self, other) -> bool:
        return self.priority >= other.priority

    ####################################################################################################################
    # Event initialization
    ####################################################################################################################

    def __init__(self, parameters: ParameterDict, arguments: Dict[str, Any]):
        """
        Initializes an event instance using a combination of the delcared event parameter names, type, and optional
        default argument values.
        :param parameters: A dictionary containing the declared event parameter names, types, and optional default
        argument values.
        :param arguments: A dictionary containing the argument values from the event creation call.
        """
        argCopy = arguments.copy()
        for key in parameters.keys():
            paramType: Optional[type] = None
            paramDefault: Optional[Any] = None
            argValue: Optional[Any] = None

            # Extract the parameter type, possible argument default value, and possible argument value.
            value = parameters[key]
            if isinstance(value, type):
                paramType = value
            else:
                if isinstance(value, tuple):
                    if isinstance(value[0], type):
                        paramType = value[0]
                    else:
                        raise TypeError('Event parameter declaration tuple [{}] be a (type, default value) tuple'.format(key))
                    if isinstance(value[1], paramType):
                        paramDefault = value[1]
                    else:
                        raise TypeError('Event parameter [[]] default value must be of the declared type [{}]'.format(key, paramType))
                else:
                    raise TypeError('Event parameter [{}] declaration must be a type or (type, default value) tuple'.format(key))

            if key in arguments:
                argValue = argCopy[key]
                del argCopy[key]
            elif paramDefault is not None:
                argValue = paramDefault
            else:
                raise RuntimeError('No value or default value for argument [{}]'.format(key))

            if isinstance(argValue, paramType):
                self[key] = argValue
            else:
                raise TypeError('Parameter [{}] must be of type [{}]'.format(key, paramType))

        if len(argCopy) != 0:
            raise RuntimeError('Extra arguments passed to event instantiation [{}]'.format(argCopy))


########################################################################################################################
# Public helper functions.
########################################################################################################################

def EventType(name: str, **kwargs) -> type:
    """
    Create an event type with the specified parameters and possible default values.
    :param name: A string which contains the name of the event. This should in most cases be the same as the name
    of the object that receives the event definition.
    :param kwargs: A parameter list which gives the event parameter names and types or type and default value as
    a tuple.
    :return : A type subclass which can be used to instantiate instances of the event.
    """
    # Determine the event priority
    priority: Optional[int] = None
    if 'priority' in kwargs:
        priority = kwargs['priority']
        del kwargs['priority']
        if not isinstance(priority, int):
            raise TypeError('priority must be an integer')
    else:
        priority = 10

    # Prepend the calling context to the name and derive the class from Event.
    stk = stack()
    prefix: str = ''
    for idx in range(1, len(stk)):
        caller: str = stk[idx][3]
        if '_' not in caller and '<' not in caller:
            prefix = caller + '.' + prefix
    mcs = type(prefix + name, (Event, ), dict(priority=priority))

    # Save the event parameter descriptions.
    mcs._setParameters(kwargs)

    return mcs
