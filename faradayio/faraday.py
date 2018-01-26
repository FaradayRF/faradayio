"""
.. module:: faraday
    :platform: Unix
    :synopsis: Main module for Faraday radios from FaradayRF.

.. moduleauthor:: Bryce Salmi <bryce@faradayrf.com>

"""

import sliplib
import pytun
import threading
import time


class Faraday(object):
    """A class that enables transfer of data between computer and Faraday

    This class interfaces a Faraday over a serial port. All it simply does is
    properly encode/decode SLIP packets.

    Attributes:
        _serialPort (serial instance): Pyserial serial port instance.
    """

    def __init__(self, serialPort=None):
        self._serialPort = serialPort

    def send(self, msg):
        """Encodes data to slip protocol and then sends over serial port

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
        """Reads in data from a serial port (length bytes), decodes SLIP packets

        A function which reads from the serial port and then uses the SlipLib
        module to decode the SLIP protocol packets. Each message received
        is added to a receive buffer in SlipLib which is then returned.

        Args:
            length (int): Length to receive with serialPort.read(length)

        Returns:
            bytes: An iterator of the receive buffer

        """

        # Create a sliplib Driver
        slipDriver = sliplib.Driver()

        # Receive data from serial port
        ret = self._serialPort.serialPort.read(length)

        # Decode data from slip format, stores msgs in sliplib.Driver.messages
        temp = slipDriver.receive(ret)
        return iter(temp)


class TunnelServer(object):
    def __init__(self, addr='10.0.0.1',
                 netmask='255.255.255.0',
                 mtu=1500,
                 name="Faraday"):
        self._tun = pytun.TunTapDevice(name=name)
        self._tun.addr = addr
        self._tun.netmask = netmask
        self._tun.mtu = mtu
        self._tun.persist(True)
        self._tun.up()

    def __del__(self):
        self._tun.down()
        print("TUN brought down...")


class Monitor(threading.Thread):
    def __init__(self, serialPort, name, addr, mtu):
        super().__init__()
        self._isRunning = threading.Event()
        self._serialPort = serialPort

        # Start a TUN adapter
        self._TUN = TunnelServer(name=name, addr=addr, mtu=mtu)

        # Create a Faraday instance
        self._faraday = Faraday(serialPort=serialPort)

    # def rxTUN(self):

    def checkTUN(self):
        packet = self._TUN._tun.read(self._TUN._tun.mtu)
        return(packet)

    def monitorTUN(self):
        """
        Check the TUN tunnel for data to send over serial
        """
        # data = self._TUN._tun.read(self._TUN._tun.mtu)

        # print(IP(data[4:]).dport)
        packet = self.checkTUN()

        if packet:
            # print("SENDING!")
            print("test3")

            try:
                # TODO Do I need to strip off [4:] before sending?
                ret = self._faraday.send(packet)
                return ret

            except AttributeError as error:
                # AttributeError was encountered
                # Tends to happen when no dport is in the packet
                print("AttributeError")

    def rxSerial(self, length):
        return(self._faraday.receive(length))

    def txSerial(self, data):
        return self._faraday.send(data)

    def checkSerial(self):
        """for item in faradayRadio.receive(res):
        Check the serialport for data to send back over the TUN tunnel
        """
        # TODO don't hardcode
        for item in self.rxSerial(1500):
            self._TUN._tun.write(item)

    def run(self):
        while not self._isRunning.is_set():
            print("test {0}\n".format(time.time()))
            self.checkTUN()
            self.checkSerial()
            time.sleep(0.1)
