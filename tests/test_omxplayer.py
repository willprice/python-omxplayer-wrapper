import unittest

from mock import patch, Mock

from pyomxplayerng.dbus_connection import DBusConnectionError
from pyomxplayerng import OMXPlayer


@patch('subprocess.Popen')
class OMXPlayerTests(unittest.TestCase):
    def test_opens_file_in_omxplayer(self, popen):
        self.patch_and_run_omxplayer()
        popen.assert_called_once_with(['omxplayer', 'test.mp4'])

    @patch('time.sleep')
    def test_tries_to_open_dbus_again_if_it_cant_connect(self, *args):
        with self.assertRaises(SystemError):
            dbus_connection = Mock(side_effect=DBusConnectionError)
            self.patch_and_run_omxplayer(Connection=dbus_connection)
            self.assertEqual(50, self.player.tries)

    # Must have the prefix 'patch' for the decorators to take effect
    def patch_and_run_omxplayer(self, Connection=Mock()):
        bus_address_finder = Mock()
        bus_address_finder.get_address = Mock(return_val="example_bus_address")
        self.player = OMXPlayer('test.mp4', bus_address_finder, Connection)
