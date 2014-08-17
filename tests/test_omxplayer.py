import unittest

from mock import patch, Mock

from nose_parameterized import parameterized

from pyomxplayerng import OMXPlayer
from pyomxplayerng.omxplayer import DBusConnection


@patch('dbus.bus.BusConnection')
class DBusConnectionTests(unittest.TestCase):
    def setUp(self):
        self.proxy = Mock()
        self.bus = Mock()
        self.bus.get_object = Mock(return_value=self.proxy)

    @parameterized.expand([
        ['unix:abstract=/tmp/dbus-EXAMPLE,guid=EXAMPLE'],
        ['unix:abstract=/tmp/dbus-EXAMPLE2,guid=EXAMPLE2'],
    ])
    def test_connects_to_omxplayer_bus(self, BusConnection, bus_address, *args):
        self.create_example_dbus_connection(bus_address)
        BusConnection.assert_called_once_with(bus_address)


    def test_constructs_proxy_for_omxplayer(self, BusConnection, *args):
        BusConnection.return_value = self.bus
        self.create_example_dbus_connection()

        self.bus.get_object.assert_called_once_with('org.mpris.MediaPlayer2.omxplayer', '/org/mpris/MediaPlayer2')

    @parameterized.expand([
        ['org.freedesktop.DBus.Properties'],
        ['org.mpris.MediaPlayer2']
    ])
    def test_constructs_dbus_interfaces(self, BusConnection, interface):
        with patch('dbus.Interface') as Interface:
            BusConnection.return_value = self.bus
            self.create_example_dbus_connection()

            Interface.assert_any_call(self.proxy, interface)

    def create_example_dbus_connection(self, address="example_bus_address"):
        DBusConnection(address)


@patch('subprocess.Popen')
class OMXPlayerTests(unittest.TestCase):
    def test_opens_file_in_omxplayer(self, popen):
        self.patch_and_run_omxplayer()
        popen.assert_called_once_with(['omxplayer', 'test.mp4'])

    # Must have the prefix 'patch' for the decorators to take effect
    def patch_and_run_omxplayer(self):
        OMXPlayer('test.mp4', connection=Mock())
