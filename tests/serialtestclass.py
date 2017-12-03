# Testing serial ports

# Import modules
import unittest.mock

class SerialTestClass(object):
    """A mock serial port test class"""
    def __init__(self):
        self._mockPort = unittest.mock.Mock()
        print("test")

    def _setPortReturnValue(self, data):
        """Sets data to be returned when mock port read"""
        self._mockPort.return_value = data

    def socketTestOne(self):
        """Simple test to make sure mock socket created successfully"""
        self._serialPort._setPortReturnValue("Hello World!")
        assert self._serialPort
