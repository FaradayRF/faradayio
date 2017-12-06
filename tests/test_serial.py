from tests.serialtestclass import SerialTestClass
# from tests.serialtestclass import Output
import asyncio
# import serial_asyncio
# import pytest_asyncio
import pytest
# import sliplib


def test_socketOne(event_loop):
    """Simple test to make sure loopback serial port created successfully"""
    serialPort = SerialTestClass()
    testStr = "Hello World!"
    serialPort.serialPort.write(testStr.encode(encoding='utf_8'))
    res = serialPort.serialPort.read(len(testStr))
    print("Loopback: {0}".format(res.decode("utf-8")))

    assert res.decode("utf-8") == testStr
