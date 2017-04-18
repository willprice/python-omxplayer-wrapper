import unittest
import sys

try: # python 2
    from mock import patch, mock_open, Mock
except ImportError:
    from unittest.mock import patch, mock_open, Mock

if sys.version_info[0] == 2:
    builtin = '__builtin__'
else:
    builtin = 'builtins'
from omxplayer.bus_finder import BusFinder

#### CONSTANTS ####
EXAMPLE_DBUS_FILE_CONTENTS = 'EXAMPLE_CONTENTS'
MOCK_OPEN = mock_open(read_data=EXAMPLE_DBUS_FILE_CONTENTS)



#### CLASSES ####
class BusFinderTests(unittest.TestCase):
    dbus_file_path = '/tmp/omxplayerdbus'

    @patch('os.path')
    @patch('omxplayer.bus_finder.glob')
    @patch('{}.open'.format(builtin), new=MOCK_OPEN)
    def test_stores_contents_of_omxplayer_dbus_file(self, *args):
        address = self.get_address()
        self.assertEqual(EXAMPLE_DBUS_FILE_CONTENTS, address)

    @patch('os.path')
    @patch('omxplayer.bus_finder.glob')
    @patch('{}.open'.format(builtin), new=MOCK_OPEN)
    def test_waits_for_file_to_exist(self, glob, mock_os_path):
        self.get_address()
        mock_os_path.isfile.assert_called_once_with(self.dbus_file_path)

    @patch('os.path')
    @patch('omxplayer.bus_finder.glob')
    @patch('{}.open'.format(builtin), new=MOCK_OPEN)
    def test_waits_for_file_to_be_written_to(self, glob, mock_os_path):
        self.get_address()
        mock_os_path.getsize.assert_called_once_with(self.dbus_file_path)

    def get_address(self):
        bus_finder = BusFinder(path=self.dbus_file_path)
        return bus_finder.get_address()
