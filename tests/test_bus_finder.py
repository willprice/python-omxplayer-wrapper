import unittest

from mock import patch, mock_open

from pyomxplayerng.bus_finder import BusFinder


EXAMPLE_DBUS_FILE_CONTENTS = 'EXAMPLE_CONTENTS'


class BusFinderTests(unittest.TestCase):
    def test_stores_contents_of_omxplayer_dbus_file(self):
        with patch('__builtin__.open', mock_open(read_data=EXAMPLE_DBUS_FILE_CONTENTS), create=True) as m:
            bus_finder = BusFinder()
            bus_finder.get_address()
            open.assert_called_once_with('/tmp/omxplayerdbus', 'r')
            self.assertEqual(EXAMPLE_DBUS_FILE_CONTENTS, bus_finder.get_address())

    def test_strips_newlines_from_file(self):
        with patch('__builtin__.open', mock_open(read_data="  " + EXAMPLE_DBUS_FILE_CONTENTS + " \n"),
                   create=True) as m:
            bus_finder = BusFinder()
            bus_finder.get_address()
            open.assert_called_once_with('/tmp/omxplayerdbus', 'r')
            self.assertEqual(EXAMPLE_DBUS_FILE_CONTENTS, bus_finder.get_address())
