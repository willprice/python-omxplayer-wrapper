import subprocess
import time
import os
import signal
from functools import wraps

import pyomxplayerng.bus_finder
from pyomxplayerng.dbus_connection import DBusConnection, DBusConnectionError


RETRY_DELAY = 0.05


class OMXPlayer(object):
    def __init__(self, filename, bus_address_finder=None, Connection=None):
        if not bus_address_finder:
            bus_address_finder = pyomxplayerng.bus_finder.BusFinder()
        if not Connection:
            Connection = DBusConnection

        self.tries = 0
        self._is_playing = True
        with open(os.devnull, 'w') as devnull:
            self._process = subprocess.Popen(['omxplayer', filename],
                                             stdout=devnull,
                                             preexec_fn=os.setsid)
        self.connection = self.setup_dbus_connection(Connection, bus_address_finder)
        self.pause()

    def setup_dbus_connection(self, Connection, bus_address_finder):
        try:
            return Connection(bus_address_finder.get_address())
        except (DBusConnectionError, IOError):
            return self.handle_failed_dbus_connection(Connection, bus_address_finder)

    def handle_failed_dbus_connection(self, Connection, bus_address_finder):
        if self.tries < 50:
            self.tries += 1
            time.sleep(RETRY_DELAY)
            return self.setup_dbus_connection(Connection, bus_address_finder)
        else:
            raise SystemError('DBus cannot connect to the OMXPlayer process')

    """ Utilities """

    def check_player_is_active(fn):
        # wraps is a decorator that improves debugging wrapped methods
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            if self._process.poll() == None:
                return fn(self, *args, **kwargs)
            else:
                print "Player is not active"

        return wrapped

    """ ROOT INTERFACE METHODS """

    @check_player_is_active
    def can_quit(self):
        return bool(self._get_root_interface().CanQuit())

    @check_player_is_active
    def can_raise(self):
        return bool(self._get_root_interface().CanRaise())

    @check_player_is_active
    def fullscreen(self):
        return bool(self._get_root_interface().FullScreen())

    @check_player_is_active
    def can_set_fullscreen(self):
        return bool(self._get_root_interface().CanSetFullscreen())

    @check_player_is_active
    def has_track_list(self):
        return bool(self._get_root_interface().HasTrackList())

    @check_player_is_active
    def identity(self):
        return str(self._get_root_interface().Identity())

    @check_player_is_active
    def supported_uri_schemes(self):
        return map(str, self._get_root_interface().SupportedUriSchemes())

    """ PLAYER INTERFACE PROPERTIES """

    @check_player_is_active
    def can_go_next(self):
        return bool(self._get_properties_interface().CanGoNext())

    @check_player_is_active
    def can_go_previous(self):
        return bool(self._get_properties_interface().CanGoPrevious())

    @check_player_is_active
    def can_seek(self):
        return bool(self._get_properties_interface().CanSeek())

    @check_player_is_active
    def can_control(self):
        return bool(self._get_properties_interface().CanControl())

    @check_player_is_active
    def can_play(self):
        return bool(self._get_properties_interface().CanPlay())

    @check_player_is_active
    def can_pause(self):
        return bool(self._get_properties_interface().CanPause())

    @check_player_is_active
    def playback_status(self):
        return str(self._get_properties_interface().PlaybackStatus())

    @check_player_is_active
    def volume(self):
        return float(self._get_properties_interface().Volume())

    @check_player_is_active
    def set_volume(self, volume):
        return float(self._get_properties_interface().Volume(volume))

    @check_player_is_active
    def mute(self):
        self._get_properties_interface().Mute()

    @check_player_is_active
    def unmute(self):
        self._get_properties_interface().Unmute()

    @check_player_is_active
    def position(self):
        return int(self._get_properties_interface().Position())

    @check_player_is_active
    def duration_us(self):
        return int(self._get_properties_interface().Duration())

    @check_player_is_active
    def duration(self):
        return self.duration_us() / (1000 * 1000.0)

    @check_player_is_active
    def minimum_rate(self):
        return float(self._get_properties_interface().MinimumRate())

    @check_player_is_active
    def maximum_rate(self):
        return float(self._get_properties_interface().MaximumRate())

    """ PLAYER INTERFACE METHODS """

    @check_player_is_active
    def next(self):
        self._get_player_interface().Next()

    @check_player_is_active
    def previous(self):
        self._get_player_interface().Previous()

    @check_player_is_active
    def pause(self):
        """
        Toggles playing state.
        """
        self._get_player_interface().Pause()

    @check_player_is_active
    def play_pause(self):
        self.pause()

    @check_player_is_active
    def stop(self):
        self._get_player_interface().Stop()

    @check_player_is_active
    def seek(self, relative_position_us):
        self._get_player_interface().Seek(relative_position_us)

    @check_player_is_active
    def set_position(self, position_us):
        self._get_player_interface().SetPosition(position_us)

    @check_player_is_active
    def list_subtitles(self):
        return map(str, self._get_player_interface().ListSubtitles())

    @check_player_is_active
    def action(self, key):
        self._get_player_interface().Action(key)

    @check_player_is_active
    def is_playing(self):
        self._is_playing = self.playback_status().lower().find('playing') != -1
        return self._is_playing

    @check_player_is_active
    def play_synch(self):
        self.play_pause()
        while self.is_playing():
            time.sleep(0.05)

    @check_player_is_active
    def play(self):
        if not self.is_playing():
            self.play_pause()

    def _get_root_interface(self):
        return self.connection.root_interface

    def _get_player_interface(self):
        return self.connection.player_interface

    def _get_properties_interface(self):
        return self.connection.properties_interface

    def quit(self):
        os.killpg(self._process.pid, signal.SIGTEM)
        self._process.wait()
