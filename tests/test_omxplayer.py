import unittest

from mock import patch, Mock
from nose_parameterized import parameterized

from pyomxplayerng import OMXPlayer


@patch('dbus.Interface')
@patch('dbus.bus.BusConnection')
@patch('subprocess.Popen')
class OMXPlayerTests(unittest.TestCase):
    def test_opens_file_in_omxplayer(self, popen, *args):
        OMXPlayer('test.mp4')
        popen.assert_called_once_with(['omxplayer', 'test.mp4'])

    @parameterized.expand([
        ['unix:abstract=/tmp/dbus-EXAMPLE,guid=EXAMPLE'],
        ['unix:abstract=/tmp/dbus-EXAMPLE2,guid=EXAMPLE2'],
    ])
    def test_connects_to_omxplayer_bus(self, popen, BusConnection, bus_address, *args):
        bus_address_finder = Mock()
        bus_address_finder.get_address = Mock(return_value=bus_address)

        OMXPlayer('test.mp4', bus_address_finder=bus_address_finder)

        BusConnection.assert_called_once_with(bus_address)

    def test_constructs_proxy_for_omxplayer(self, popen, BusConnection, *args):
        mock_bus = Mock()
        mock_bus.get_object = Mock()
        BusConnection.return_value = mock_bus
        bus_address_finder = Mock()
        bus_address_finder.get_address = Mock(return_value="example_bus_address")

        OMXPlayer('test.mp4', bus_address_finder=bus_address_finder)

        mock_bus.get_object.assert_called_once_with('org.mpris.MediaPlayer2.omxplayer', '/org/mpris/MediaPlayer2')

    @parameterized.expand([
        ['org.freedesktop.DBus.Properties'],
        ['org.mpris.MediaPlayer2']
    ])
    def test_constructs_dbus_interfaces(self, popen, BusConnection, Interface, interface):
        proxy = Mock()
        bus = Mock()
        bus.get_object = Mock(return_value=proxy)
        BusConnection.return_value = bus
        bus_address_finder = Mock()
        bus_address_finder.get_address = Mock(return_value="example_bus_address")

        OMXPlayer('test.mp4', bus_address_finder=bus_address_finder)

        Interface.assert_any_call(proxy, interface)

