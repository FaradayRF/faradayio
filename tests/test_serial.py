import pytest
import sliplib
import string

from faradayio import faraday
# from tests.serialtestclass import SerialTestClass


def test_socketOne():
    """Simple test to make sure loopback serial port created successfully"""
    serialInstance = faraday.SerialTestClass()
    testStr = "Hello World!"
    serialInstance.serialPort.write(testStr.encode(encoding='utf_8'))
    res = serialInstance.serialPort.read(len(testStr))

    assert res.decode("utf-8") == testStr


@pytest.mark.parametrize("test_input", [
    (b""),
    (bytes(string.ascii_letters, "utf-8")),
    (bytes(string.ascii_uppercase, "utf-8")),
    (bytes(string.ascii_lowercase, "utf-8")),
    (bytes(string.digits, "utf-8")),
    (bytes(string.hexdigits, "utf-8")),
    (bytes(string.printable, "utf-8")),
    (bytes(string.octdigits, "utf-8")),
    (sliplib.slip.END),
    (sliplib.slip.END*2),
    (sliplib.slip.ESC),
    (sliplib.slip.ESC*2),
    (sliplib.slip.ESC_ESC),
    (sliplib.slip.ESC_ESC*2),
    (sliplib.slip.ESC_END),
    (sliplib.slip.ESC_END*2),
])
def test_serialParamaterizedSynchSend(test_input):
    # Create class object necessary for test
    serialInstance = faraday.SerialTestClass()
    faradayRadio = faraday.Faraday(serialInstance.serialPort)

    # Create slip message to test against
    slipMsg = sliplib.encode(test_input)

    # Send data over Faraday
    res = faradayRadio.send(test_input)

    # Use serial to receive raw transmission with slip protocol
    ret = serialInstance.serialPort.read(res)

    # Check that the returned data from the serial port == slipMsg
    assert ret == slipMsg


@pytest.mark.parametrize("test_input", [
    (b""),
    (bytes(string.ascii_letters, "utf-8")),
    (bytes(string.ascii_uppercase, "utf-8")),
    (bytes(string.ascii_lowercase, "utf-8")),
    (bytes(string.digits, "utf-8")),
    (bytes(string.hexdigits, "utf-8")),
    (bytes(string.printable, "utf-8")),
    (bytes(string.octdigits, "utf-8")),
    (sliplib.slip.END),
    (sliplib.slip.END*2),
    (sliplib.slip.ESC),
    (sliplib.slip.ESC*2),
    (sliplib.slip.ESC_ESC),
    (sliplib.slip.ESC_ESC*2),
    (sliplib.slip.ESC_END),
    (sliplib.slip.ESC_END*2),
])
def test_serialParamaterizedSynchReceive(test_input):
    """
    Tests a synchronous faradayio receive command with data. This should read
    in data, convert it to slip format, libraryand return the original message
    """

    # Create class object necessary for test
    serialInstance = faraday.SerialTestClass()
    slip = sliplib.Driver()
    faradayRadio = faraday.Faraday(serialInstance.serialPort)

    # Create slip message to test against
    slipMsg = slip.send(test_input)

    # Use serial to send raw transmission with slip protocol
    res = serialInstance.serialPort.write(slipMsg)

    # Receive data from Faraday which yields each item it parses from slip
    for item in faradayRadio.receive(res):
        # Should be only one item
        assert item == test_input
