import sliplib
import asyncio
import serial_asyncio

class Faraday(object):
    """A class that enables transfer of data between computer and Faraday"""
    def __init__(self, serialPort=None):
        self._serialPort = serialPort

    def send(self, msg: bytes):
        """Converts data to slip format then sends over serial port"""
        # Create a sliplib Driver
        slipDriver = sliplib.Driver()

        # Package data in slip format
        slipData = slipDriver.send(msg)

        # Send data over serial port
        res = self._serialPort.serialPort.write(slipData)

        # Return number of bytes transmitted over serial port
        return res

    def receive(self, length):
        """Reads in data from a serial port (length bytes), decodes slip"""

        # Create a sliplib Driver
        slipDriver = sliplib.Driver()

        # Receive data from serial port
        ret = self._serialPort.serialPort.read(length)

        # Decode data from slip format, stores msgs in sliplib.Driver.messages
        slipDriver.receive(ret)

        # Yield each message as a generator
        for item in slipDriver.messages:
            yield item

    async def handle_serialRecieve(serialPort):
        """Handle a serial connection"""
        req = await serialPort.receive(1024)
        print(req)
        serialPort.close()

class FaradayInput(asyncio.Protocol):
    def __init__(self):
        super().__init__()
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport

    def data_received(self, data):
        self._transport.write(data)

class Input(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport

    def data_received(self, data):
        self._transport.write(data)

class Output(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        self._transport = None
        self.received = []
        self.actions = []
        self.TEXT = b'Hello, World!\n'

    def connection_made(self, transport):
        self._transport = transport
        self.actions.append('open')
        transport.write(self.TEXT)

    def data_received(self, data):
        self.received.append(data)
        if b'\n' in data:
            self._transport.close()
        return data

    def connection_lost(self, exc):
        self.actions.append('close')
        self._transport.loop.stop()

    def pause_writing(self):
        self.actions.append('pause')
        print(self._transport.get_write_buffer_size())

    def resume_writing(self):
        self.actions.append('resume')
        print(self._transport.get_write_buffer_size())
