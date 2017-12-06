# Testing serial ports

# Import modules
#from unittest.mock import MagicMock
import asyncio
from unittest.mock import Mock

class SerialTestClass(object):
    """A mock serial port test class"""
    def __init__(self):
        """Creates a mock serial port object with read function"""
        self.read = Mock()

    def _setPortReadValue(self, data):
        """Sets data to be returned when mock port read"""
        self.read.return_value = data
