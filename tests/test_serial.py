from tests.serialtestclass import SerialTestClass
# from tests.serialtestclass import Output
import asyncio
# import serial_asyncio
# import pytest_asyncio
import pytest
import sliplib
import faradayio


def test_socketOne(event_loop):
    """Simple test to make sure loopback serial port created successfully"""
    serialPort = SerialTestClass()
    testStr = "Hello World!"
    serialPort.serialPort.write(testStr.encode(encoding='utf_8'))
    res = serialPort.serialPort.read(len(testStr))
    print("Loopback: {0}".format(res.decode("utf-8")))

    assert res.decode("utf-8") == testStr

def test_serialEmptySynchronousSend():
        """
        Tests a synchronous faradayio send command with empty data. This
        should take in data convert it to slip format and send it out to the
        serial port.
        """

        serialPort = SerialTestClass()
        slip = sliplib.Driver()
        faraday = faradayio.Faraday(serialPort)

        emptyStr = ""
        # testStr = "abcdefghijklmnopqrstuvwxyz0123456789"

        # Create slip message to test against
        slipMsg = slip.send(emptyStr.encode(encoding='utf_8'))

        # Send data over Faraday
        # Function should take in data, convert to utf-8 string, and return
        # a slip encoded string. Function should return number of bytest sent
        # including slip protocol overhead
        res = faraday.send(emptyStr)

        # Use serial to receive raw transmission with slip protocol
        ret = serialPort.read(res)

        # Check that the returned data from the serial port == slipMsg
        assert slipMsg == ret
