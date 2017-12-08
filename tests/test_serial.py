from tests.serialtestclass import SerialTestClass
# from tests.serialtestclass import Output
import asyncio
# import serial_asyncio
# import pytest_asyncio
import pytest
import sliplib
from faradayio import faraday


def test_socketOne(event_loop):
    """Simple test to make sure loopback serial port created successfully"""
    serialPort = SerialTestClass()
    testStr = "Hello World!"
    serialPort.serialPort.write(testStr.encode(encoding='utf_8'))
    res = serialPort.serialPort.read(len(testStr))

    assert res.decode("utf-8") == testStr

def test_serialEmptySynchronousSend():
        """
        Tests a synchronous faradayio send command with empty data. This
        should take in data convert it to slip format and send it out to the
        serial port.
        """

        # Create class object necessary for test
        serialPort = SerialTestClass()
        slip = sliplib.Driver()
        faradayRadio = faraday.Faraday(serialPort)

        # Create empty string test message
        emptyStr = ""

        # Create slip message to test against
        slipMsg = slip.send(emptyStr.encode(encoding='utf_8'))

        # Send data over Faraday
        res = faradayRadio.send(emptyStr)

        # Use serial to receive raw transmission with slip protocol
        ret = serialPort.serialPort.read(res)

        # Check that the returned data from the serial port == slipMsg
        assert slipMsg == ret

def test_serialStrSynchronousSend():
        """
        Tests a synchronous faradayio send command with string data. This
        should take in data convert it to slip format and send it out to the
        serial port.
        """

        # Create class object necessary for test
        serialPort = SerialTestClass()
        slip = sliplib.Driver()
        faradayRadio = faraday.Faraday(serialPort)

        # Create string test message
        testStr = "abcdefghijklmnopqrstuvwxyz0123456789"

        # Create slip message to test against
        slipMsg = slip.send(testStr.encode(encoding='utf_8'))

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
        emptyStr = ""

        # Create slip message to test against
        slipMsg = slip.send(emptyStr.encode(encoding='utf_8'))

        # Use serial to send raw transmission with slip protocol
        res = serialPort.serialPort.write(slipMsg)

        # Receive data from Faraday which yields each item it parses from slip
        for item in faradayRadio.receive(res):
            # Should be only one item
            assert item.decode("utf-8") == emptyStr
