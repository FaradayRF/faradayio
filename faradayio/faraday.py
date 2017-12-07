import sliplib

class Faraday(object):
    """A class that enables transfer of data between computer and Faraday"""
    def __init__(self, serialPort=None):
        self._serialPort = serialPort

    def send(self, msg):
        """Converts data to slip format then sends over serial port"""
        # Create a sliplib Driver
        slipDriver = sliplib.Driver()

        # Convert data to UTF-8 encoding
        msg = msg.encode(encoding="utf-8")

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

        # Decode data from slip format
        data = slipDriver.receive(ret)

        return data
