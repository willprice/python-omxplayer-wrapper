import unittest
import os

from nose_parameterized import parameterized
from mock import patch, Mock, call, mock_open

from omxplayer.dbus_connection import DBusConnectionError
from omxplayer.player import OMXPlayer
from omxplayer.player import OMXPLAYER_ARGS


m = mock_open()


@patch('time.sleep')
@patch('subprocess.Popen')
class OMXPlayerTests(unittest.TestCase):
    @patch('__builtin__.open', m)
    def test_opens_file_in_omxplayer(self, popen, *args):
        self.patch_and_run_omxplayer()
        popen.assert_called_once_with(
            ['omxplayer'] + OMXPLAYER_ARGS + ['test.mp4'],
            preexec_fn=os.setsid, stdout=m())

    @patch('time.sleep')
    def test_tries_to_open_dbus_again_if_it_cant_connect(self, *args):
        with self.assertRaises(SystemError):
            dbus_connection = Mock(side_effect=DBusConnectionError)
            self.patch_and_run_omxplayer(Connection=dbus_connection)
            self.assertEqual(50, self.player.tries)


    @parameterized.expand([
        ['can_quit', 'CanQuit'],
        ['fullscreen', 'FullScreen'],
        ['can_set_fullscreen', 'CanSetFullscreen'],
        ['can_raise', 'CanRaise'],
        ['has_track_list', 'HasTrackList'],
        ['identity', 'Identity']
    ])
    def test_root_interface_commands(self, popen, sleep, command_name,
                                     interface_command_name, *args):
        self.patch_and_run_omxplayer()
        self.patch_interface_and_run_command('_get_root_interface',
                                             command_name,
                                             interface_command_name, *args)

    @parameterized.expand([
        ['next', 'Next'],
        ['previous', 'Previous'],
        ['pause', 'Pause'],
        ['stop', 'Stop'],
        ['seek', 'Seek', 100],
        ['set_position', 'SetPosition', 100000],
        ['list_subtitles', 'ListSubtitles'],
        ['action', 'Action', 'p']
    ])
    def test_player_interface_commands(self, popen, sleep, command_name,
                                       interface_command_name, *args):
        self.patch_and_run_omxplayer()
        self.patch_interface_and_run_command('_get_player_interface',
                                             command_name,
                                             interface_command_name, *args)

    @parameterized.expand([
        ['can_go_next', 'CanGoNext'],
        ['can_go_previous', 'CanGoPrevious'],
        ['can_play', 'CanPlay'],
        ['can_seek', 'CanSeek'],
        ['can_control', 'CanControl'],
        ['playback_status', 'PlaybackStatus'],
        ['volume', 'Volume'],
        ['mute', 'Mute'],
        ['unmute', 'Unmute'],
        ['position', 'Position'],
        ['duration', 'Duration'],
        ['minimum_rate', 'MinimumRate'],
        ['maximum_rate', 'MaximumRate'],
    ])
    def test_properties_interface_commands(self, popen, sleep, command_name,
                                           interface_command_name, *args):
        self.patch_and_run_omxplayer()
        self.patch_interface_and_run_command('_get_properties_interface',
                                             command_name,
                                             interface_command_name, *args)

    def test_quitting_waits_for_omxplayer_to_die(self, popen, *args):
        omxplayer_process = Mock()
        popen.return_value = omxplayer_process
        self.patch_and_run_omxplayer()

        with patch('omxplayer.player.os'):
            self.player.quit()

        omxplayer_process.wait.assert_any_call()

    def test_check_process_still_exists_before_dbus_call(self, *args):
        self.patch_and_run_omxplayer()
        self.player._process = process = Mock(return_value=None)
        process.poll.return_value = None

        self.player.can_quit()

        process.poll.assert_called_once_with()


    def patch_interface_and_run_command(self, interface_name,
                                        command_name, interface_command_name,
                                        *command_args):
        self.player._process.poll = Mock(return_value=None)
        with patch.object(self.player, interface_name) as interface:
            self.run_command(command_name, *command_args)
            # generates a call of the form `call().CanQuit`
            expected_call = getattr(call(), interface_command_name)(
                *command_args)
            interface.assert_has_calls(expected_call)

    def run_command(self, command_name, *args):
        command = getattr(self.player, command_name)
        command(*args)

    # Must have the prefix 'patch' for the decorators to take effect
    def patch_and_run_omxplayer(self, Connection=Mock()):
        bus_address_finder = Mock()
        bus_address_finder.get_address = Mock(return_val="example_bus_address")
        self.player = OMXPlayer('test.mp4', bus_address_finder, Connection)
