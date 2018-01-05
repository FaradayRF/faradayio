import pytest
import pytun
import socket
import time
import os
import sliplib
import string
import struct
import binascii
import dpkt

from faradayio import faraday
from scapy.all import IP, UDP

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
    s.send(b'Hello, world')
    time.sleep(0.1)
    data = faradayTUN._tun.read(faradayTUN._tun.mtu)
    print(UDP(IP(data[4:]).load))

    s.close()
