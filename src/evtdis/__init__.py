"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""
name = "evtdis"

__all__ = [
    "Dispatcher",
    "Event",
    "EventType",
    "ParameterDict",
    "Publisher",
    "EventCallback",
    "__version__",
]

from .Dispatcher import Dispatcher
from .Event import Event
from .Event import EventType
from .Event import ParameterDict
from .Publisher import Publisher
from .Publisher import EventCallback
from .__about__ import __version__

