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
import subprocess
import threading

from faradayio import faraday
from tests.serialtestclass import SerialTestClass
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
    """
    Start a TUN adapter and send a message through it. This tests sending ascii
    over a socket connection through the TUN while using pytun to receive the
    data and check that the IP payload is valid with scapy.
    """
    # Start a TUN adapter
    faradayTUN = faraday.TunnelServer()

    #sudo sysctl -w net.ipv6.conf.all.autoconf=0
    #subprocess.run('sudo sysctl -w net.ipv6.conf.Faraday.autoconf=0', shell=True, stderr=subprocess.PIPE)


    # Send a string throught the IP
    HOST = faradayTUN._tun.dstaddr
    PORT = 9999 #  Anything

    # Just send asci lprintable data for now
    msg = bytes(string.printable, "utf-8")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((HOST,PORT))
    s.send(msg)
    s.close()

    # Loop through packets received until packet is received from correct port
    while True:
        data = faradayTUN._tun.read(faradayTUN._tun.mtu)

        try:
            if(IP(data[4:]).dport == PORT):
                # print(IP(data[4:]).show())
                break

        except AttributeError as error:
            pass
            # AttributeError was encountered
            # Tends to happen when no dport is in the packet
            # print("AttributeError")


    # Remove the first four bytes from the data since there is an ethertype
    # header that should not be there from pytun
    payload = IP(data[4:]).load

    # Check that slip message was sent correctly over TunnelServer
    assert msg == payload


def test_tunSlipSend():
    """
    Test SLIP data sent over the TUN adapter.

    Start a TUN adapter and send data over it while a thread runs to receive
    data sent over the tunnel and promptly send it over a serial port which is
    running a serial loopback test. Ensures data at the end of the loopback
    test is valid.
    """
    # Create a test serial port
    serialPort = SerialTestClass()
    #
    # Configure the TUN adapter and socket port we aim to use to send data on
    HOST = '10.0.0.2'
    PORT = 9999 #  Anything

    # TODO: Start the monitor thread
    isRunning = threading.Event()
    TUNMonitor = faraday.Monitor(isRunning=isRunning, serialPort=serialPort)
    TUNMonitor._isRunning = isRunning
    TUNMonitor.start()
    # time.sleep(0.5) # Temporary

    # Just send asci lprintable data for now#
    # msg = bytes(string.printable, "utf-8")
    msg = bytes("Hello, world!", "utf-8")
    # time.sleep(10)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((HOST,PORT))
    s.send(msg)
    time.sleep(1)

    # # TODO: Read data back from TUN adapter after monitor thread loops it back
    # rxmsg = s.recv(1500)
    # print(rxmsg)
    #
    # # Stop the threaded monitor
    # time.sleep(1)
    isRunning.set()
    s.close()

    # Check that slip message was sent correctly over TunnelServer
    # assert msg == response
