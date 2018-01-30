# FaradayIO
[![Build Status](https://travis-ci.org/FaradayRF/faradayio.svg?branch=master)](https://travis-ci.org/FaradayRF/faradayio)
[![Coverage Status](https://coveralls.io/repos/github/FaradayRF/faradayio/badge.svg?branch=master)](https://coveralls.io/github/FaradayRF/faradayio?branch=master)

The `faradayio` module provides a [TUN/TAP](https://en.wikipedia.org/wiki/TUN/TAP) interface which tunnels network traffic in [SLIP](https://en.wikipedia.org/wiki/Serial_Line_Internet_Protocol) format over a serial port. This was originally designed for the [Faraday](https://faradayrf.com/faraday/) radio but the software is radio agnostic. By default this module helps create a TUN/TAP adapter on the `10.0.0.0` network and a simple command line program is also provided to automatically setup a network adapter for a Faraday radio.

## Installation
Installation is simple. If you are just installing to use with a radio then the pypi installation is all you need. However, if you are looking to develop code then you should install from a GitHub repository clone in editable mode. Please note we suggest installing with a [virtual environment](https://github.com/FaradayRF/faradayio/wiki/Working-With-Python3-Virtual-Environments) in all cases!
### PyPi
To install `faradayio` simply install with `pip3`
```
pip3 install faradayio
```
### Git Repository Editable Mode
To install `faradayio` from a git repository in editable mode simple checkout from GitHub and use `pip3` to install in editable mode.

```
$ git clone git@github.com:FaradayRF/faradayio.git
$ cd faradayio
$ pip3 install -e .
```

## Usage
_Placeholder for command line program completion. This should also have some module use examples as well but that will wait until this module is actually used to create a working program._

## Wiki
Please use our [faradayio wiki](https://github.com/FaradayRF/faradayio/wiki) to find helpful tips on installation, setting up a development environment, and running unit tests.

## FaradayRF
This project is provided by [FaradayRF](https://www.faradayrf.com) as [GPLv3](https://github.com/FaradayRF/faradayio/blob/master/LICENSE) software aimed at the amateur radio (ham radio) community. Please join us on our [Gitter lobby](https://gitter.im/FaradayRF/Lobby) if you have any questions. Send an email to [Support@faradayrf.com](Support@faradayrf.com) if you would like to contact us via email.
