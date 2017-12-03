from tests.serialtestclass import SerialTestClass

def test_socketOne():
    """Simple test to make sure mock socket created successfully"""
    serialPort = SerialTestClass()
    serialPort._setPortReturnValue("Hello World!")
    assert serialPort is not None
