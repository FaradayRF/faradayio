import pytest
import pytun
import socket
import time
import os
import sliplib
import string
import struct

from faradayio import faraday

def test_tunSetup():
    """Setup a Faraday TUN and check initialized values"""
    faradayTUN = faraday.TunnelServer()

    # Check defaults
    assert faradayTUN._tun.name == 'Faraday'
    assert faradayTUN._tun.addr == '10.0.0.1'
    assert faradayTUN._tun.netmask == '255.255.255.0'
    assert faradayTUN._tun.mtu == 1500

def test_tunStart():
    """Start a Faraday TUN adapter and ping it"""
    faradayTUN = faraday.TunnelServer()
    response = os.system("ping -c 1 10.0.0.1")

    # Check that response == 0 which means TUN adapter started
    assert response == 0

def test_tunSend():
    """Start a TUN adapter and send a SLIP message from IP"""
    # Start a TUN adapter
    faradayTUN = faraday.TunnelServer()
    # faradayTUN._tun.mtu = 100

    # Send a string throught the IP
    HOST = faradayTUN._tun.dstaddr
    PORT = 9999 #  Anything

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # time.sleep(60)
    s.connect((HOST,PORT))
    while True:
        s.sendall(b'Hello, world')
        time.sleep(0.1)
    print(s)
    # num = s.sendto(bytes("Hello, world!","utf-8"),(HOST,PORT))
    # print(num)
    # faradayTUN._tun.write(bytes("Hello, world!","utf-8"))
    # while True:
    #     faradayTUN._tun.write("Hello, world!")
    #     # print("wrote...")
    #     time.sleep(0.01)
    #     data = faradayTUN._tun.read(faradayTUN._tun.mtu)
    #     # print(data)
    s.close()
    # print(len(data))
    # print(bytes.fromhex(str(data)))
    # string = struct.unpack("50sH",data)
    # print(string)
    # for i in string:
    #     print(i)



    # # Create class object necessary for test
    # serialPort = SerialTestClass()
    # faradayRadio = faraday.Faraday(serialPort)
    #
    # # Create slip message to test against
    # slipMsg = sliplib.encode(test_input)
