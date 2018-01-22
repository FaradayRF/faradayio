import pytest
import pytun
import socket
import time
import os
import sliplib
import string
import struct
import binascii
# import dpkt
import subprocess
import threading

from faradayio import faraday
from tests.serialtestclass import SerialTestClass
from scapy.all import *

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
    sourceHost = '10.0.0.1'
    sourcePort = 9998
    destHost = '10.0.0.2'
    destPort = 9999 #  Anything

    # TODO: Start the monitor thread
    TUNMonitor = faraday.Monitor(serialPort=serialPort, name="Faraday", addr=sourceHost, dstaddr=destHost)

    srcPacket = IP(dst=destHost, src=sourceHost)/UDP(sport=sourcePort, dport=destPort)

    #
    # Test TUN adapter obtaining packets
    #

    # Use scapy to send packet over Faraday
    # TODO Don't hardcode
    sendp(srcPacket,iface="Faraday")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((sourceHost,sourcePort))
    s.send(b"Hello, world!")
    s.close()
    # Manually check TUN adapter for packets in the tunnel
    # This is necessary because the threads are not running this
    while True:
        # Loop through packets until correct packet is returned
        packet = TUNMonitor.checkTUN()
        if packet:
            if IP(packet[4:]).dst == destHost:
                # Check that packet got through TUN without error
                break
    # Obtained IP packet to destination IP so check that it hasn't changed
    assert packet[4:] == srcPacket.__bytes__()

    #
    # Test SLIP encoding/decoding of IP packet over serial port in loopback mode
    #

    # Send IP packet over serial port.
    bytesSent = TUNMonitor.txSerial(packet)
    assert bytesSent is not None    #  We expect some data sent
    assert bytesSent > len(packet)  # We expect SLIP encoding to add bytes

    # TODO Don't hardcode
    # Receive data over serial port and check packets for test IP packet
    rxBytes = TUNMonitor.rxSerial(1500)
    for item in rxBytes:
        # Iterate through packets and check for packet to destination IP
        if IP(item[4:]).dst == destHost:
            # Found IP packet to destination so break from loop
            break

    # Check that the packet received over the serial loopback is the same as sent
    assert item[4:] == packet[4:]

def test_serialToTUN():
    """
    Test serial port to TUN link. Don't need a serial port but just assume that
    an IP packet was received from the serial port and properly decoded with
    SLIP. Send it to the TUN and verify that the IP:PORT receives the message.
    """
    # Create a test serial port for TUN Monitor class. Won't be used.
    serialPort = SerialTestClass()

    # Configure TUN IP:PORT and IP Packet source IP:PORT parameters for test
    sourceAddress = '10.0.0.2'
    sourcePort = 9998
    tunAddress = '10.0.0.1'
    tunPort = 9999

    # Start a TUN Monitor class
    TUNMonitor = faraday.Monitor(serialPort=serialPort, name="Faraday",addr=tunAddress,dstaddr=sourceAddress)

    # Open a socket for UDP packets and bind it to the TUN address:port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('10.0.0.1', 9999))

    # Create simple IP packet with message. Send to TUN address:port
    message = bytes("Hello, World! {0}".format(time.time()),"utf-8")
    etherType = b"\x00\x00\x08\x00"
    packet = etherType + (IP(dst=tunAddress, src=sourceAddress)/UDP(sport=sourcePort, dport=tunPort)/message).__bytes__()

    # Write a simple message over the TUN, no need for checker thread
    TUNMonitor._TUN._tun.write(packet)

    # Receive data from the socket bound to the TUN address:port
    data, address = s.recvfrom(4096)

    # Check that data written to TUN matches data received from socket
    assert data == message

    # Close the socket
    s.close()
