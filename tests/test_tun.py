import pytest
import pytun

from faradayio import faraday

def test_tunSetup():
    """Setup a Faraday TUN and check initialized values"""
    faradayTUN = faraday.TunnelServer()

    # Check defaults
    assert faradayTUN._addr == '10.0.1.0'
    assert faradayTUN._dstaddr == ''
    assert faradayTUN._netmask == '255.255.0.0'
    assert faradayTUN._mtu == 1500


# self._tun.up()
# self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# self._sock.bind((laddr, lport))
# self._raddr = raddr
# self._rport = rport
