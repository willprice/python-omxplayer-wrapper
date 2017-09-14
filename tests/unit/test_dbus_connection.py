import unittest

from parameterized import parameterized
from mock import patch, Mock
from dbus import DBusException

from omxplayer.dbus_connection import DBusConnection, DBusConnectionError


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

        self.bus.get_object.assert_called_once_with(
            'org.mpris.MediaPlayer2.omxplayer',
            '/org/mpris/MediaPlayer2',
            introspect=False)

    @parameterized.expand([
        ['org.mpris.MediaPlayer2'],
        ['org.mpris.MediaPlayer2.Player'],
        ['org.freedesktop.DBus.Properties']
    ])
    def test_constructs_dbus_interfaces(self, BusConnection, interface):
        with patch('dbus.Interface') as Interface:
            BusConnection.return_value = self.bus
            self.create_example_dbus_connection()

            Interface.assert_any_call(self.proxy, interface)

    def test_constructs_root_interface(self, *args):
        with patch('dbus.Interface') as Interface:
            mpris_interface = Mock()
            Interface.return_value = mpris_interface
            connection = self.create_example_dbus_connection()
            self.assertEqual(mpris_interface, connection.root_interface)

    def test_constructs_properties_interface(self, *args):
        with patch('dbus.Interface') as Interface:
            properties_interface = Mock()
            Interface.return_value = properties_interface
            connection = self.create_example_dbus_connection()
            self.assertEqual(properties_interface,
                             connection.properties_interface)

    def test_constructs_player_interface(self, *args):
        with patch('dbus.Interface') as Interface:
            player_interface = Mock()
            Interface.return_value = player_interface
            connection = self.create_example_dbus_connection()
            self.assertEqual(player_interface, connection.player_interface)

    def test_raises_error_if_cant_obtain_proxy(self, BusConnection):
        self.bus.get_object = Mock(side_effect=DBusException)
        BusConnection.return_value = self.bus
        with self.assertRaises(DBusConnectionError):
            connection = self.create_example_dbus_connection()

    def create_example_dbus_connection(self, address="example_bus_address"):
        return DBusConnection(address)
