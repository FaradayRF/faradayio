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
    isRunning = threading.Event()
    TUNMonitor = faraday.Monitor(isRunning=isRunning, serialPort=serialPort)

    srcPacket = IP(dst=destHost, src=sourceHost)/UDP(sport=sourcePort, dport=destPort)

    #
    # Test TUN adapter obtaining packets
    #

    # Use scapy to send packet over Faraday
    # TODO Don't hardcode
    sendp(srcPacket,iface="Faraday")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((HOST,PORT))
    s.send(msg)
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
    SLIP.
    """
    # Create a test serial port
    serialPort = SerialTestClass()
    serialPort2 = SerialTestClass()


    #
    # Configure the TUN adapter and socket port we aim to use to send data on
    sourceHost = '10.0.0.1'
    sourcePort = 9998
    destHost = '10.0.0.2'
    destPort = 9999 #  Anything

    # TODO: Start the monitor thread
    isRunning = threading.Event()
    TUNMonitor = faraday.Monitor(isRunning=isRunning, serialPort=serialPort, name="Faraday",addr=sourceHost,dstaddr=destHost)
    TUNMonitor2 = faraday.Monitor(isRunning=isRunning, serialPort=serialPort2, name="Faraday2",addr=destHost,dstaddr=sourceHost)

    os.system('ip link set Faraday up')
    os.system('ip address add 10.0.0.1/32 dev Faraday')
    os.system('ip route add 10.0.0.2 dev Faraday')
    os.system('ip address add 10.0.0.2/32 dev Faraday2')
    os.system('ip route add 10.0.0.1 dev Faraday2')

    srcPacket = IP(dst=destHost, src=sourceHost)/UDP(sport=sourcePort, dport=destPort)/"Hello, World!"
    srcPacket2 = IP(dst=sourceHost, src=destHost)/UDP(sport=destPort, dport=sourcePort)/"Hello, World2!"

    #
    # Test TUN adapter obtaining packets
    #

    # Use scapy to send packet over Faraday
    # TODO Don't hardcode
    # while True:

        # time.sleep(0.1)
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.connect((sourceHost,sourcePort))
    # s.send(msg)
    # s.close()
    # Manually check TUN adapter for packets in the tunnel
    # This is necessary because the threads are not running this

    while True:
        # print("Looping...")
        sendp(srcPacket2,iface="Faraday")
        # sendp(srcPacket2,iface="Faraday")
        # Loop through packets until correct packet is returned
        packet = TUNMonitor.checkTUN()
        if packet:
            print(packet)
            # IP(packet[4:]).show()
            TUNMonitor2._TUN._tun.write(packet)
    # Obtained IP packet to destination IP so check that it hasn't changed
    # assert packet[4:] == srcPacket.__bytes__()





    # while True:
    #     # Loop through packets until correct packet is returned
    #     packet = TUNMonitor.checkTUN()
    #     if packet:
    #         if IP(packet[4:]).dst == destHost:
    #             # Check that packet got through TUN without error
    #             break
    # # Obtained IP packet to destination IP so check that it hasn't changed
    # assert packet[4:] == srcPacket.__bytes__()





    #
    # Test SLIP encoding/decoding of IP packet over serial port in loopback mode
    #

    # Send IP packet over second TUN device
    # IP(packet[4:]).show()
    # Ether(packet).show()

    # Configure the TUN adapter and socket port we aim to use to send data on
    # sourceHost = '10.0.0.2'
    # sourcePort = 9999
    # destHost = '10.0.0.1'
    # destPort = 9998 #  Anything

    # TUNMonitor2 = faraday.Monitor(isRunning=isRunning, serialPort=serialPort2, name="Faraday2", addr=sourceHost,dstaddr=destHost)
    #
    # os.system('ip link set Faraday2 up')
    # os.system('ip address add 10.0.0.2/24 dev Faraday2')
    # os.system('ip route add 10.0.0.2/24 dev Faraday2')
    #
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.connect((sourceHost,sourcePort))
    # print(s)
    # # s.send(msg)
    # # s.close()
    #
    # # while True:
    # TUNMonitor._TUN._tun.write(packet)
    # IP(packet[4:]).show()
    # time.sleep(0.1)
    # print("receiving")
    #
    # rxPacket = s.recv(150)
    # # rxPacket = TUNMonitor2.checkTUN()
    # print(rxPacket)
    # isRunning = False
    # s.close()
