import subprocess
import time

import pyomxplayerng.bus_finder
from pyomxplayerng.dbus_connection import DBusConnection, DBusConnectionError


RETRY_DELAY = 0.05


class OMXPlayer(object):
    def __init__(self, filename, bus_address_finder=None, Connection=None):
        self.tries = 0
        self._is_playing = True
        self._process = subprocess.Popen(['omxplayer', filename])
        self.connection = self.setup_dbus_connection(Connection, bus_address_finder)
        self.pause()

    def setup_dbus_connection(self, Connection, bus_address_finder):
        if not Connection:
            Connection = DBusConnection
        if not bus_address_finder:
            bus_address_finder = pyomxplayerng.bus_finder.BusFinder()
        try:
            return Connection(bus_address_finder.get_address())
        except DBusConnectionError, IOError:
            connection = None
            return self.handle_failed_dbus_connection(Connection, bus_address_finder)

    def handle_failed_dbus_connection(self, Connection, bus_address_finder):
        if self.tries < 50:
            self.tries += 1
            time.sleep(RETRY_DELAY)
            return self.setup_dbus_connection(Connection, bus_address_finder)
        else:
            raise SystemError('DBus cannot connect to the OMXPlayer process')


    """ ROOT INTERFACE METHODS """

    def can_quit(self):
        return bool(self._get_root_interface().CanQuit())

    def can_raise(self):
        return bool(self._get_root_interface().CanRaise())

    def fullscreen(self):
        return bool(self._get_root_interface().FullScreen())

    def can_set_fullscreen(self):
        return bool(self._get_root_interface().CanSetFullscreen())

    def has_track_list(self):
        return bool(self._get_root_interface().HasTrackList())

    def identity(self):
        return str(self._get_root_interface().Identity())

    def supported_uri_schemes(self):
        return map(str, self._get_root_interface().SupportedUriSchemes())

    """ PLAYER INTERFACE PROPERTIES """

    def can_go_next(self):
        return bool(self._get_properties_interface().CanGoNext())

    def can_go_previous(self):
        return bool(self._get_properties_interface().CanGoPrevious())

    def can_seek(self):
        return bool(self._get_properties_interface().CanSeek())

    def can_control(self):
        return bool(self._get_properties_interface().CanControl())

    def can_play(self):
        return bool(self._get_properties_interface().CanPlay())

    def can_pause(self):
        return bool(self._get_properties_interface().CanPause())

    def playback_status(self):
        return str(self._get_properties_interface().PlaybackStatus())

    def volume(self):
        return float(self._get_properties_interface().Volume())

    def set_volume(self, volume):
        return float(self._get_properties_interface().Volume(volume))

    def mute(self):
        self._get_properties_interface().Mute()

    def unmute(self):
        self._get_properties_interface().Unmute()

    def position(self):
        return int(self._get_properties_interface().Position())

    def duration_us(self):
        return int(self._get_properties_interface().Duration())

    def duration(self):
        return self.duration_us() / (1000 * 1000.0)

    def minimum_rate(self):
        return float(self._get_properties_interface().MinimumRate())

    def maximum_rate(self):
        return float(self._get_properties_interface().MaximumRate())


    """ PLAYER INTERFACE METHODS """

    def next(self):
        self._get_player_interface().Next()

    def previous(self):
        self._get_player_interface().Previous()

    def pause(self):
        """
        Toggles playing state.
        """
        self._get_player_interface().Pause()

    def play_pause(self):
        self.pause()

    def stop(self):
        self._get_player_interface().Stop()

    def seek(self, relative_position_us):
        self._get_player_interface().Seek(relative_position_us)

    def set_position(self, position_us):
        self._get_player_interface().SetPosition(position_us)

    def list_subtitles(self):
        return map(str, self._get_player_interface().ListSubtitles())

    def action(self, key):
        self._get_player_interface().Action(key)

    def is_playing(self):
        self._is_playing = self.playback_status().lower().find('playing') != -1
        return self._is_playing

    def play_synch(self):
        self.play_pause()
        while self.is_playing():
            time.sleep(0.05)

    def play(self):
        if not self.is_playing():
            self.play_pause()

    def _get_root_interface(self):
        return self.connection.root_interface

    def _get_player_interface(self):
        return self.connection.player_interface

    def _get_properties_interface(self):
        return self.connection.properties_interface
