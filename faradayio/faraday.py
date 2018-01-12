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
from scapy.all import IP, UDP

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
        temp = slipDriver.receive(ret)
        # print(temp)

        # Yield each message as a generator
        # print("Returned: {0}".format(ret))
        for item in temp:
            # print("item {0}".format(item))
            yield item


class TunnelServer(object):
    def __init__(self, addr='10.0.0.1', dstaddr='10.0.0.2', netmask='255.255.255.0', mtu=1500):
        self._tun = pytun.TunTapDevice(name='Faraday')
        self._tun.addr = addr
        self._tun.dstaddr = dstaddr
        self._tun.netmask = netmask
        self._tun.mtu = mtu
        self._tun.persist(True)
        self._tun.up()

    def __del__(self):
        self._tun.down()
        print("TUN brought down...")


class Monitor(threading.Thread):
    def __init__(self, isRunning, serialPort):
        super().__init__()
        self._isRunning = isRunning
        self._serialPort = serialPort

        # Start a TUN adapter
        self._TUN = TunnelServer()

        # Create a Faraday instance
        self._faraday = Faraday(serialPort=serialPort)

    def checkTUN(self):
        """
        Check the TUN tunnel for data to send over serial
        """
        data = self._TUN._tun.read(self._TUN._tun.mtu)
        # IP(data[4:]).show()
        # print(IP(data[4:]).dport)

        if data:
            # print("SENDING!")

            try:
                # if(IP(data[4:]).dport == 9999):
                IP(data[4:]).show()
                # print("checkTUN:\n{0}\n{1}".format(IP(data[4:]).summary(),IP(data[4:]).load))
                # TODO Do I need to strip off [4:] before sending?
                ret = self._faraday.send(data)
                print("Sent {0} bytes over serial...".format(ret))
                return ret

            except AttributeError as error:
                # AttributeError was encountered
                # Tends to happen when no dport is in the packet
                print("AttributeError")

    def checkSerial(self):
        """for item in faradayRadio.receive(res):
        Check the serialport for data to send back over the TUN tunnel
        """
        # print("checking serial!")
        # Does this need to be smart about how long/length to read?
        # print(next(self._faraday.receive(1500)))
        for item in self._faraday.receive(1500):
            IP(item[4:]).show()
            # print("message: {0}".format(item))
            self._TUN._tun.write(item)

    def run(self):
        while not self._isRunning.is_set():
            print("test {0}\n".format(time.time()))
            self.checkTUN()
            self.checkSerial()
            time.sleep(0.1)
