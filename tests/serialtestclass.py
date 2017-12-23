# Testing serial ports

# Import modules
import asyncio
import serial
import serial_asyncio


class SerialTestClass(object):
    """A mock serial port test class"""
    def __init__(self):
        """Creates a mock serial port which is a loopback object"""
        self._port = "loop://"
        self._timeout = 0
        self._baudrate = 115200
        self.serialPort = \
            serial.serial_for_url(url=self._port,
                                  timeout=self._timeout,
                                  baudrate=self._baudrate)
        self.asyncSerialPort = \
            serial_asyncio.open_serial_connection(url=self._port,
                                                  timeout=self._timeout,
                                                  baudrate=self._baudrate)

    def _run(coro):
        """Run the coroutine"""
        return asyncio.get_event_loop().run_until_complete(coro)
