import pytest
import pytun
import socket
import time
import os

from faradayio import faraday

def test_tunSetup():
    """Setup a Faraday TUN and check initialized values"""
    faradayTUN = faraday.TunnelServer()

    # Check defaults
    assert faradayTUN._tun.name == 'Faraday'
    assert faradayTUN._tun.addr == '10.0.1.0'
    assert faradayTUN._tun.netmask == '255.255.0.0'
    assert faradayTUN._tun.mtu == 1500

def test_tunStart():
    """Start a Faraday TUN adapter and ping it"""
    faradayTUN = faraday.TunnelServer()
    response = os.system("ping -c 1 10.0.1.0")

    # Check that response == 0 which means TUN adapter started
    assert response == 0
    
