"""
.. module:: faraday
    :platform: Unix
    :synopsis: Main module for Faraday radios from FaradayRF.

.. moduleauthor:: Bryce Salmi <bryce@faradayrf.com>

"""

import sliplib
import pytun
import threading
import serial
import timeout_decorator

import serial.tools.list_ports


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
        res = self._serialPort.write(slipData)

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
        ret = self._serialPort.read(length)

        # Decode data from slip format, stores msgs in sliplib.Driver.messages
        temp = slipDriver.receive(ret)
        return iter(temp)


class TunnelServer(object):
    """
    A class which creates a TUN/TAP device for Faraday uses.

    Creates a basic TUN/TAP adapter with generic values for use with Faraday.
    Also provides a method to close TUN/TAP when the class is destroyed.

    Attributes:
        addr: IP address of TUN/TAP adapter
        netmask: Netmask of TUN/TAP adapter
        mtu: Maximum Transmission Unit for TUN/TAP adapter
        name: Name of TUN/TAP adapter
    """
    def __init__(self, addr,
                 netmask,
                 mtu,
                 name):
        self._tun = pytun.TunTapDevice(name=name)
        self._tun.addr = addr
        self._tun.netmask = netmask
        self._tun.mtu = mtu

        # Set TUN persistance to True and bring TUN up
        self._tun.persist(True)
        self._tun.up()

    def __del__(self):
        """
        Clean up TUN when the TunnelServer class is destroyed
        """
        self._tun.down()
        print("TUN brought down...")


class Monitor(threading.Thread):
    """
    A class which inherits from threading.Thread to provide TUN/TAP monitors

    Inherits from threading.Thread and is designed to be run as a thread. This
    provides functions which can be used to monitor the TUN/TAP adapter and
    send/receive data when it arrives over TUN or serial.

    Attributes:
        serialPort: Pyserial instance for a serial port
        isRunning: Threading event to signal thread exit
        name: Name of TUN/TAP device to be created by the monitor
        addr: IP address of the TUN/TAP device to be created
        mtu: Maximum Transmission Unit of TUN/TAP adapter TODO delete?
    """
    def __init__(self,
                 serialPort,
                 isRunning,
                 name="Faraday",
                 addr='10.0.0.1',
                 netmask='255.255.255.0',
                 mtu=1500):
        super().__init__()
        self.isRunning = isRunning
        self._serialPort = serialPort

        # Start a TUN adapter
        self._TUN = TunnelServer(name=name,
                                 addr=addr,
                                 netmask=netmask,
                                 mtu=mtu)

        # Create a Faraday instance
        self._faraday = Faraday(serialPort=serialPort)

    @timeout_decorator.timeout(1, use_signals=False)
    def checkTUN(self):
        """
        Checks the TUN adapter for data and returns any that is found.

        Returns:
            packet: Data read from the TUN adapter
        """
        packet = self._TUN._tun.read(self._TUN._tun.mtu)
        return(packet)

    def monitorTUN(self):
        """
        Monitors the TUN adapter and sends data over serial port.

        Returns:
            ret: Number of bytes sent over serial port
        """
        packet = self.checkTUN()

        if packet:
            try:
                # TODO Do I need to strip off [4:] before sending?
                ret = self._faraday.send(packet)
                return ret

            except AttributeError as error:
                # AttributeError was encounteredthreading.Event()
                print("AttributeError")

    def rxSerial(self, length):
        """
        Checks the serial port for data and returns any that is found.

        Args:
            length: Number of bytes to read from serial port

        Returns:
            data: Data received from serial port
        """
        return(self._faraday.receive(length))

    def txSerial(self, data):
        """
        Sends data over serial port.

        Args:
            data: Data to be sent over serial port

        Returns:
            length: Number of bytes sent over serial port
        """
        return self._faraday.send(data)

    def checkSerial(self):
        """
        Check the serial port for data to write to the TUN adapter.
        """
        for item in self.rxSerial(self._TUN._tun.mtu):
            # print("about to send: {0}".format(item))
            try:
                self._TUN._tun.write(item)
            except pytun.Error as error:
                print("pytun error writing: {0}".format(item))
                print(error)

    def run(self):
        """
        Wrapper function for TUN and serial port monitoring

        Wraps the necessary functions to loop over until self._isRunning
        threading.Event() is set(). This checks for data on the TUN/serial
        interfaces and then sends data over the appropriate interface. This
        function is automatically run when Threading.start() is called on the
        Monitor class.
        """
        while self.isRunning.is_set():
            try:
                try:
                    # self.checkTUN()
                    self.monitorTUN()

                except timeout_decorator.TimeoutError as error:
                    # No data received so just move on
                    pass
                self.checkSerial()
            except KeyboardInterrupt:
                break


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

    def isPortAvailable(port='/dev/ttyUSB0'):
        '''
        Checks whether specified port is available.

        Source code derived from @lqdev suggestion per #38

        Args:
            port: Serial port location i.e. 'COM1'. Default is /dev/ttyUSB0

        Returns:
            available: Boolean value indicating presence of port
        '''
        isPortAvailable = serial.tools.list_ports.grep(port)

        try:
            next(isPortAvailable)
            available = True
        except StopIteration:
            available = False

        return available
