# Testing serial ports

# Import modules
import asyncio
from unittest.mock import Mock

class SerialTestClass(object):
    """A mock serial port test class"""
    def __init__(self):
        """Creates a mock serial port object with read function"""
        self._readVal = Mock()

    def _setPortReadValue(self, data):
        """Sets data to be returned when mock port read"""
        self._readVal.return_value = data

    async def read(self):
        """Mimics pyserial read() function"""
        return self._readVal()

class Output(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
        transport.serial.rts = False
        transport.write(b'hello world\n')

    def data_received(self, data):
        print('data received', repr(data))
        self.transport.close()

    def connection_lost(self, exc):
        print('port closed')
        asyncio.get_event_loop().stop()
