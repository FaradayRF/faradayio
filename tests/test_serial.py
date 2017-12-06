from tests.serialtestclass import SerialTestClass
# from tests.serialtestclass import Output
import asyncio
# import serial_asyncio
import pytest_asyncio
import pytest
# import sliplib


@pytest.mark.asyncio
async def test_socketOne(event_loop):
    """Simple test to make sure mock socket created successfully"""
    serialPort = SerialTestClass()
    serialPort._setPortReadValue("my string")

    assert await serialPort.read() == "my string"
