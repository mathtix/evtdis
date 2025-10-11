# Thread Safe Event Dispatcher for Python
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?logo=python)]()
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Platforms](https://img.shields.io/badge/Windows%20%7C%20Linux-supported-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

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

## Build
### Tool Dependencies
#### pipx
``` bash
 sudo apt update
 sudo apt install pipx
```
#### Hatch
``` bash
pipx install hatch
```
### Build Command Sequence
First create a hatch environment.
``` bash
hatch env create
hatch shell
```
Run the build, test, lint and coverage.
``` bash
hatch build
hatch run dev:test
hatch run dev:lint
hatch run dev:cov
```

## Publish
<!-- pipx run twine upload --repository testpypi dist/* -->
``` bash
 hatch publish -r [test/main]
```

### PYPI RC File
The format of PYPI "run commands" (rc) file (~/.pypirc) is:
```
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-<TOKEN>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-<TOKEN>
```
Replace `pypi-<TOKEN>` with a token generated in the Account Settings section of the respective pipy site.

<!--
```bash
 python -m twine check dist/*
 python -m twine upload --repository testpypi dist/*
```
-->

