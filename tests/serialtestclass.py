# Testing serial ports

# Import modules
import asyncio
import serial
from unittest.mock import Mock

class SerialTestClass(object):
    """A mock serial port test class"""
    def __init__(self):
        """Creates a mock serial port which is a loopback object"""
        self._port = "loop://"
        self._timeout = 0
        self._baudrate = 115200
        self.serialPort = \
            serial.serial_for_url(  url=self._port,
                                    timeout=self._timeout,
                                    baudrate=self._baudrate)
