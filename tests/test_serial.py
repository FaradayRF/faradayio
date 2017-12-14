from tests.serialtestclass import SerialTestClass
# from tests.serialtestclass import Output
import asyncio
import serial_asyncio
# import pytest_asyncio
import pytest
import sliplib
from faradayio import faraday
from faradayio.faraday import FaradayInput
import unittest
# from faradayio.faraday import FaradayOutput


def test_socketOne(event_loop):
    """Simple test to make sure loopback serial port created successfully"""
    serialPort = SerialTestClass()
    testStr = "Hello World!"
    serialPort.serialPort.write(testStr.encode(encoding='utf_8'))
    res = serialPort.serialPort.read(len(testStr))

    assert res.decode("utf-8") == testStr

# @pytest.mark.parametrize("test_input", [
#     (b""),
#     # (b"abcdefghijklmnopqrstuvwxyz0123456789"),
#     # (b"test" + sliplib.slip.END + b"test"),
# ])
def test_serialParamaterizedSynchSend():
    # Create class object necessary for test
    serialPort = SerialTestClass()
    slip = sliplib.Driver()
    faradayRadio = faraday.Faraday(serialPort)

    # Create empty string test message
    # testStr = test_input

    # Create slip message to test against
    slipMsg = sliplib.encode(b"test")
    print(slipMsg)
    #
    # # Send data over Faradayb
    # bytes()
    # res = faradayRadio.send(b"test")
    #
    # # Use serial to receive raw transmission with slip protocol
    # ret = serialPort.serialPort.read(res)
    #
    # # Check that the returned data from the serial port == slipMsg
    # assert ret == slipMsg

def test_serialStrSynchronousSend():
        """
        Tests a synchronous faradayio send command with string data. This
        should take in data co()
        faradayRadio = faradanvert it to slip format and send it out to the
        serial port.
        """

        # Create class object necessary for test
        serialPort = SerialTestClass()
        slip = sliplib.Driver()
        faradayRadio = faraday.Faraday(serialPort)

        # Create string test message
        testStr = b"abcdefghijklmnopqrstuvwxyz0123456789"

        # Create slip message to test against
        slipMsg = slip.send(testStr)

        # Send data over Faraday
        res = faradayRadio.send(testStr)

        # Use serial to receive raw transmission with slip protocol
        ret = serialPort.serialPort.read(res)

        # Check that the returned data from the serial port == slipMsg
        assert slipMsg == ret

def test_serialEmptySynchronousReceive():
        """
        Tests a synchronous faradayio receive command with empty data. This
        should read in data, convert it to slip format, and return the original
        message
        """

        # Create class object necessary for test
        serialPort = SerialTestClass()
        slip = sliplib.Driver()
        faradayRadio = faraday.Faraday(serialPort)

        # Create empty string test message
        emptyStr = b""

        # Create slip message to test against
        slipMsg = slip.send(emptyStr)

        # Use serial to send raw transmission with slip protocol
        res = serialPort.serialPort.write(slipMsg)

        # Receive data from Faraday which yields each item it parses from slip
        for item in faradayRadio.receive(res):
            # Should be only one item
            assert item.decode("utf-8") == emptyStr

def test_serialStrSynchronousReceive():
        """
        Tests a synchronous faradayio receive command with empty data. This
        should read in data, convert it to slip format, and return the original
        message
        """

        # Create class object necessary for test
        serialPort = SerialTestClass()
        slip = sliplib.Driver()
        faradayRadio = faraday.Faraday(serialPort)

        # Create test string test message
        testStr = b"abcdefghijklmnopqrstuvwxyz0123456789"

        # Create slip message to test against
        slipMsg = slip.send(testStr)

        # Use serial to send raw transmission with slip protocol
        res = serialPort.serialPort.write(slipMsg)

        # Receive data from Faraday which yields each item it parses from slip
        for item in faradayRadio.receive(res):
            # Should be only one item
            assert item == testStr

import os
import unittest
import asyncio

import serial_asyncio

HOST = '127.0.0.1'
_PORT = 8888

# on which port should the tests be performed:
PORT = 'socket://%s:%s' % (HOST, _PORT)


@unittest.skipIf(os.name != 'posix', "asyncio not supported on platform")
class Test_asyncio(unittest.TestCase):
    """Test asyncio related functionality"""

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        # create a closed serial port

    def tearDown(self):
        self.loop.close()

    def test_asyncio(self):
        faradayIn = faraday.Input
        faradayOut = faraday.Output
        if PORT.startswith('socket://'):
            coro = self.loop.create_server(faradayIn, HOST, _PORT)
            self.loop.run_until_complete(coro)

        client = serial_asyncio.create_serial_connection(self.loop, faradayOut, PORT)
        self.loop.run_until_complete(asyncio.gather(client))
        # print("TEST = {0}".format(test))
        self.loop.run_forever()
        # self.assertEqual(b''.join(client.received), faraday.Output.TEXT)
        # self.assertEqual(actions, ['open', 'close'])
