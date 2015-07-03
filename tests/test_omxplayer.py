import unittest
import os
import signal
import dbus

from nose_parameterized import parameterized
from mock import patch, Mock, call, mock_open

from omxplayer.dbus_connection import DBusConnectionError
from omxplayer.player import OMXPlayer


MOCK_OPEN = mock_open()


@patch('__builtin__.open', MOCK_OPEN)
@patch('os.killpg')
@patch('os.path.isfile')
@patch('time.sleep')
@patch('subprocess.Popen')
class OMXPlayerTests(unittest.TestCase):
    TEST_FILE_NAME = "./test.mp4"

    def test_opens_file_in_omxplayer(self, popen, *args):
        self.patch_and_run_omxplayer()
        popen.assert_called_once_with(
            ['omxplayer', './test.mp4'],
            preexec_fn=os.setsid, stdout=MOCK_OPEN())

    @patch('time.sleep')
    def test_tries_to_open_dbus_again_if_it_cant_connect(self, *args):
        # TODO: Shouldn't this be DBusConnectionError not SystemError
        with self.assertRaises(SystemError):
            dbus_connection = Mock(side_effect=DBusConnectionError)
            self.patch_and_run_omxplayer(Connection=dbus_connection)
            self.assertEqual(50, self.player.tries)


    @parameterized.expand([
        ['can_quit', 'CanQuit', [], []],
        ['can_set_fullscreen', 'CanSetFullscreen', [], []],
        ['identity', 'Identity', [], []]
    ])
    def test_root_interface_commands(self, popen, sleep, isfile, killpg, command_name,
                                     interface_command_name, *args):
        self.patch_and_run_omxplayer()
        self.patch_interface_and_run_command('_get_root_interface',
                                             command_name,
                                             interface_command_name, *args)

    @parameterized.expand([
        ['pause', 'Pause', [], []],
        ['stop', 'Stop', [], []],
        ['seek', 'Seek', [100], [100]],
        ['set_position', 'SetPosition', [1], [dbus.ObjectPath("/not/used"),
                                              dbus.Int64(1000000L)]],
        ['list_subtitles', 'ListSubtitles', [], []],
        ['action', 'Action', ['p'], ['p']]
    ])
    def test_player_interface_commands(self, popen, sleep, isfile, killpg, command_name,
                                       interface_command_name, *args):
        self.patch_and_run_omxplayer()
        self.patch_interface_and_run_command('_get_player_interface',
                                             command_name,
                                             interface_command_name, *args)

    @parameterized.expand([
        ['can_play', 'CanPlay', [], []],
        ['can_seek', 'CanSeek', [], []],
        ['can_control', 'CanControl', [], []],
        ['playback_status', 'PlaybackStatus', [], []],
        ['volume', 'Volume', [], []],
        ['mute', 'Mute', [], []],
        ['unmute', 'Unmute', [], []],
        ['position', 'Position', [], []],
        ['duration', 'Duration', [], []],
        ['minimum_rate', 'MinimumRate', [], []],
        ['maximum_rate', 'MaximumRate', [], []],
    ])
    def test_properties_interface_commands(self, popen, sleep, isfile, killpg, command_name,
                                           interface_command_name, *args):
        self.patch_and_run_omxplayer()
        self.patch_interface_and_run_command('_get_properties_interface',
                                             command_name,
                                             interface_command_name, *args)

    def test_quitting(self, popen, sleep, isfile, killpg, *args):
        omxplayer_process = Mock()
        popen.return_value = omxplayer_process
        self.patch_and_run_omxplayer()
        self.player.quit()
        killpg.assert_called_once_with(omxplayer_process.pid, signal.SIGTERM)

    def test_quitting_waits_for_omxplayer_to_die(self, popen, sleep, isfile, killpg, *args):
        omxplayer_process = Mock()
        popen.return_value = omxplayer_process
        self.patch_and_run_omxplayer()
        self.player.quit()
        # There should be one call for the monitor process and an additional
        # call for when we wait for the process to die
        omxplayer_process.wait.assert_has_calls([call() for _ in range(2)])

    def test_check_process_still_exists_before_dbus_call(self, *args):
        self.patch_and_run_omxplayer()
        self.player._process = process = Mock(return_value=None)
        process.poll.return_value = None

        self.player.can_quit()

        process.poll.assert_called_once_with()

    def test_checks_media_file_exists_before_launching_player(self, *args):
        with patch('os.path') as ospath:
            self.patch_and_run_omxplayer()
            ospath.isfile.assert_called_once_with(self.TEST_FILE_NAME)

    @unittest.skip("Haven't written test yet")
    def test_set_position_checks_to_see_if_position_is_less_than_length(self, *args):
        self.patch_and_run_omxplayer()
        #self.player.set_position()



    def patch_interface_and_run_command(self, interface_name,
                                        command_name, interface_command_name,
                                        command_args,
                                        expected_args):
        self.player._process.poll = Mock(return_value=None)
        with patch.object(self.player, interface_name) as interface:
            self.run_command(command_name, *command_args)
            # generates a call of the form `call().CanQuit`
            expected_call = getattr(call(), interface_command_name)(*expected_args)
            interface.assert_has_calls(expected_call)

    def run_command(self, command_name, *args):
        command = getattr(self.player, command_name)
        command(*args)

    # Must have the prefix 'patch' for the decorators to take effect
    def patch_and_run_omxplayer(self, Connection=Mock()):
        bus_address_finder = Mock()
        bus_address_finder.get_address.return_val = "example_bus_address"
        self.player = OMXPlayer(self.TEST_FILE_NAME,
                                bus_address_finder=bus_address_finder,
                                Connection=Connection,
                                cleaner=Mock())
