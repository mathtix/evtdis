# Thread Safe Event Dispatcher for Python
The evtdis Python package provides a thread safe mechanism for communicating
between python threads running in parallel. The package contains three primary
classes.
* Event
* Publisher
* Dispatcher

### Event Class
The event class is a python meta-type class that provides a means for
defining named events with typed parameters.

### Publisher
The publisher class provides a frame-work for advertising events to which
dispatcher subclass instances can subscribe for delivery when the events
are published.

### Dispatcher
The dispatcher class derives from the Python Thread class and acts as a
thread-safe intermediary between publishers and subscribers.
When a dispatcher receives an event from from a publisher on the publisher's
thread of execution, the event goes into a thread-safe queue. The event is
then dispatched to the subclass event processing function on the dispatcher's
thread of execution.

### Examples
Currently the best examples are the package tests and other MathTix python
packages which make use of the evtdis package.

### Dependencies
#### Package
The evtdis package does not require dependencies beyond the packages contained
in the Python standard library.

#### Build
 * pipx
 * hatch

### Hatch
``` bash
pipx install hatch
```

### Isolated Build Environment
``` bash
hatch env create
hatch shell
```

### Commands
``` bash
hatch build
hatch run dev:test
hatch run dev:lint
hatch run dev:cov
```

<!-- pipx run twine upload --repository testpypi dist/* -->