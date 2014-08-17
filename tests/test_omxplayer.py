import unittest

from mock import patch, Mock

from pyomxplayerng import OMXPlayer


@patch('subprocess.Popen')
class OMXPlayerTests(unittest.TestCase):
    def test_opens_file_in_omxplayer(self, popen):
        self.patch_and_run_omxplayer()
        popen.assert_called_once_with(['omxplayer', 'test.mp4'])

    # Must have the prefix 'patch' for the decorators to take effect
    def patch_and_run_omxplayer(self):
        OMXPlayer('test.mp4', connection=Mock())
