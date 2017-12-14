import sliplib


class Faraday(object):
    """A class that enables transfer of data between computer and Faraday"""
    def __init__(self, serialPort=None):
        self._serialPort = serialPort

    def send(self, msg: bytes):
        """Converts data to slip format then sends over serial port"""
        # Create a sliplib Driver
        slipDriver = sliplib.Driver()

        # Package data in slip format
        slipData = slipDriver.send(msg)

        # Send data over serial port
        res = self._serialPort.serialPort.write(slipData)

        # Return number of bytes transmitted over serial port
        return res

    def receive(self, length):
        """Reads in data from a serial port (length bytes), decodes slip"""

        # Create a sliplib Driver
        slipDriver = sliplib.Driver()

        # Receive data from serial port
        ret = self._serialPort.serialPort.read(length)

        # Decode data from slip format, stores msgs in sliplib.Driver.messages
        slipDriver.receive(ret)

        # Yield each message as a generator
        for item in slipDriver.messages:
            yield item
