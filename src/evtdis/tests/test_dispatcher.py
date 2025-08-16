"""
Copyright(c) 2025-present, MathTix, LLC.
Distributed under the MIT License (http://opensource.org/licenses/MIT)
"""

import logging.config
from os import path
from time import sleep
from unittest import TestCase
from evtdis import EventType
from evtdis import Dispatcher

log_file = path.join(path.dirname(path.abspath(__file__)), 'testlog.conf')
logging.config.fileConfig(fname=log_file, disable_existing_loggers=False)
_LOGGER = logging.getLogger(__name__)


class Generator(Dispatcher):

    class Input():
        CmdOne = EventType(name='CmdOne', a=tuple)
        CmdTwo = EventType(name='CmdTwo', boy=str, girl=str)

    class Internal():
        One = EventType(name='One', arg1=int)
        Two = EventType(name='Two', arg3=float, arg4=list)

    class Output():
        OutOne = EventType(name='OutOne', x=tuple)
        OutTwo = EventType(name='OutTwo', man=str, woman=str)

    def __init__(self) -> None:
        Dispatcher.__init__(self, name="Generator")
        self.eventOneArgs: dict = {'arg1': 4}
        self.eventTwoArgs: dict = {'arg3': 8.0, 'arg4': [1, 2, 3]}

        self.eventOneArgsMatch: bool = False
        self.eventTwoArgsMatch: bool = False

        self.runningEventCalled: bool = False
        self.eventIdleCalled: bool = False
        self.exitingEventCalled: bool = False

        # Start and exit processing.
        self.startEventType = Dispatcher.Evt.Running
        self.exitEventType = Dispatcher.Evt.Exiting
        self._subscribeInternalEvent(eventType=Dispatcher.Evt.Running, call=self.runningCB)
        self._subscribeInternalEvent(eventType=Dispatcher.Evt.Exiting, call=self.exitingCB)

    def addInternalEventProcessing(self) -> None:
        self._subscribeInternalEvent(eventType=Generator.Internal.One, call=self.internalEventOneCB)
        self._subscribeInternalEvent(eventType=Generator.Internal.Two, call=self.internalEventTwoCB)

    def addCommandEventProcessing(self) -> None:
        self._subscribeInputEvent(eventType=Generator.Input.CmdOne, call=self.cmdEventOneCB)
        self._subscribeInputEvent(eventType=Generator.Input.CmdTwo, call=self.cmdEventTwoCB)

    def addOutputEvents(self) -> None:
        self._registerOutputEvent(eventType=Generator.Output.OutOne)
        self._registerOutputEvent(eventType=Generator.Output.OutTwo)

    def addIdleProcessing(self) -> None:
        self.idleEventType = Dispatcher.Evt.Idle
        self._subscribeInternalEvent(eventType=Dispatcher.Evt.Idle, call=self.idleCB)

    def triggerInternalEvents(self) -> None:
        self._publishInternalEvent(event=Generator.Internal.One(**self.eventOneArgs))
        self._publishInternalEvent(event=Generator.Internal.Two(**self.eventTwoArgs))

    def runningCB(self) -> None:
        _LOGGER.debug('Generator runningCB called')
        self.runningEventCalled = True

    def idleCB(self) -> None:
        _LOGGER.debug('Generator idleCB called')
        self.eventIdleCalled = True

    def exitingCB(self) -> None:
        _LOGGER.debug('Generator exitingCB called')
        self.exitingEventCalled = True

    def internalEventOneCB(self, arg1: int) -> None:
        _LOGGER.debug('Generator internalEventOneCB called')
        if self.eventOneArgs == {'arg1': arg1}:
            self.eventOneArgsMatch = True

    def internalEventTwoCB(self, arg3: float, arg4: list) -> None:
        _LOGGER.debug('Generator internalEventTwoCB called')
        if self.eventTwoArgs == {'arg3': arg3, 'arg4': arg4}:
            self.eventTwoArgsMatch = True

    def cmdEventOneCB(self, a: tuple) -> None:
        _LOGGER.debug('Generator cmdEventOneCB called a = %s', a)
        self._publishExternalEvent(event=Generator.Output.OutOne(x=a))

    def cmdEventTwoCB(self, boy: str, girl: str) -> None:
        _LOGGER.debug('Generator cmdEventTwoCB called boy = %s girl = %s', boy, girl)
        self._publishExternalEvent(event=Generator.Output.OutTwo(man=boy, woman=girl))


class Target(Dispatcher):

    def __init__(self, source: Dispatcher) -> None:
        Dispatcher.__init__(self, name='Target')

        self.source: Dispatcher = source

        self.eventOneArgs: tuple = None
        self.eventTwoArgs: tuple = None

        # Start and exit processing.
        self.exitEventType = Dispatcher.Evt.Exiting
        self._subscribeInternalEvent(eventType=Dispatcher.Evt.Exiting)

    def addOutputCommandProcessing(self) -> None:
        self.subscribeToRemoteOutputEvent(eventType=Generator.Output.OutOne,
                                          source=self.source, call=self.receiveGeneratorOneCB)

        self.subscribeToRemoteOutputEvent(eventType=Generator.Output.OutTwo,
                                          source=self.source, call=self.receiveGeneratorTwoCB)

    def receiveGeneratorOneCB(self, x: tuple) -> None:
        _LOGGER.debug('Target receiveGeneratorOneCB called x = %s', x)
        self.eventOneArgs = {'a': x}

    def receiveGeneratorTwoCB(self, man: str, woman: str) -> None:
        _LOGGER.debug('Target receiveGeneratorOneCB called man = %s woman = %s', man, woman)
        self.eventTwoArgs = {'boy': man, 'girl': woman}


class TestDispatcher(TestCase):

    def __init__(self, methodName='runTest') -> None:
        TestCase.__init__(self, methodName=methodName)
        self.generator: Generator = None
        self.target: Target = None

    def setUp(self) -> None:
        self.generator = Generator()
        self.target = Target(source=self.generator)

    def tearDown(self) -> None:
        del self.generator
        del self.target

    def test_startingExitingEvents(self) -> None:
        _LOGGER.debug('Testing start processing')
        self.generator.start()
        self.generator.triggerExit()
        self.generator.join()
        self.assertEqual(True, self.generator.runningEventCalled)
        self.assertEqual(True, self.generator.exitingEventCalled)

    def test_idleEvent(self) -> None:
        _LOGGER.debug('Testing idle processing')
        self.generator.start()
        self.generator.addIdleProcessing()
        # Sleep to allow some idle events to occur.
        # This number must be bigger then the idle wake up time duration.
        sleep(0.1)
        self.generator.triggerExit()
        self.generator.join()
        self.assertEqual(True, self.generator.eventIdleCalled)

    def test_internalEvents(self) -> None:
        _LOGGER.debug('Testing internal event processing')
        self.generator.addInternalEventProcessing()
        self.generator.start()
        self.generator.triggerInternalEvents()
        self.generator.triggerExit()
        self.generator.join()
        self.assertEqual(True, self.generator.eventOneArgsMatch)
        self.assertEqual(True, self.generator.eventTwoArgsMatch)

    def test_inputEvents(self) -> None:
        _LOGGER.debug('Testing command event processing')
        self.generator.addCommandEventProcessing()
        self.generator.addOutputEvents()
        self.target.addOutputCommandProcessing()
        self.generator.start()
        self.target.start()

        argsOne = {'a': (1, 2, 3)}
        self.generator.deliverInputEvent(event=Generator.Input.CmdOne(**argsOne))
        argsTwo = {'boy': 'Fred', 'girl': 'Mary'}
        self.generator.deliverInputEvent(event=Generator.Input.CmdTwo(**argsTwo))

        self.generator.triggerExit()
        self.generator.join()

        self.target.triggerExit()
        self.target.join()

        self.assertEqual(argsOne, self.target.eventOneArgs)
        self.assertEqual(argsTwo, self.target.eventTwoArgs)
