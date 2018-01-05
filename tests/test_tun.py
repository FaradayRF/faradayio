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
    # May not even need SLIP here as the next step involves slip over serial port....


    # Start a TUN adapter
    faradayTUN = faraday.TunnelServer()

    # Send a string throught the IP
    HOST = faradayTUN._tun.dstaddr
    PORT = 9999 #  Anything

    # Just send asci letters for now
    msg = bytes(string.ascii_letters, "utf-8")
    slipData = sliplib.encode(msg)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((HOST,PORT))
    s.send(slipData)

    data = faradayTUN._tun.read(faradayTUN._tun.mtu)
    # Check for IPV4 since IPV6 packets sometime come down
    # print(IP(data[4:]).version == 6)
    payload = IP(data[4:]).load

    decodedmsg = sliplib.decode(payload)
    # print(message)

    # Check that slip message was sent correctly over TunnelServer
    assert slipData == payload

    # Check that message was decoded from slip correctly
    assert msg == decodedmsg
    s.close()
