"""
.. module:: faraday
    :platform: Unix
    :synopsis: Main module for Faraday radios from FaradayRF.

.. moduleauthor:: Bryce Salmi <bryce@faradayrf.com>

"""

import sliplib
import pytun


class Faraday(object):
    """A class that enables transfer of data between computer and Faraday

    Attributes:
        _serialPort (serial instance): Pyserial serial port instance.
    """

    def __init__(self, serialPort=None):
        self._serialPort = serialPort

    def send(self, msg):
        """Converts data to slip format then sends over serial port

        Uses the SlipLib module to convert the message data into SLIP format.
        The message is then sent over the serial port opened with the instance
        of the Faraday class used when invoking send().

        Args:
            msg (bytes): Bytes format message to send over serial port.

        Returns:
            int: Number of bytes transmitted over the serial port.

        """
        # Create a sliplib Driver
        slipDriver = sliplib.Driver()

        # Package data in slip format
        slipData = slipDriver.send(msg)

        # Send data over serial port
        res = self._serialPort.serialPort.write(slipData)

        # Return number of bytes transmitted over serial port
        return res

    def receive(self, length):
        """Reads in data from a serial port (length bytes), decodes slip

        A generator function which reads the serial port opened with the
        instance of Faraday used to read() and then uses the SlipLib module to
        convert the SLIP format into bytes. Each message received is added to a
        receive buffer in SlipLib which is then yielded.

        Args:
            length (int): Length to receive with serialPort.read(length)

        Yields:
            bytes: The next message in the receive buffer

        """

        # Create a sliplib Driver
        slipDriver = sliplib.Driver()

        # Receive data from serial port
        ret = self._serialPort.serialPort.read(length)

        # Decode data from slip format, stores msgs in sliplib.Driver.messages
        slipDriver.receive(ret)

        # Yield each message as a generator
        for item in slipDriver.messages:
            yield item

class TunnelServer(object):
    def __init__(self, addr='10.0.1.0', netmask='255.255.0.0', mtu=1500):
        self._tun = pytun.TunTapDevice(name='Faraday')
        self._tun.addr = addr
        self._tun.netmask = netmask
        self._tun.mtu = mtu
        self._tun.up()

    def __del__(self):
        self._tun.down()
        print("TUN brought down...")
