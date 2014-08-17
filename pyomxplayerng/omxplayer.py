import subprocess
import time

import pyomxplayerng.bus_finder
from pyomxplayerng.dbus_connection import DBusConnection, DBusConnectionError


class OMXPlayer(object):
    def __init__(self, filename, bus_address_finder=None, Connection=None):
        self.tries = 0
        self._process = subprocess.Popen(['omxplayer', filename])
        self.connection = self.setup_dbus_connection(Connection, bus_address_finder)

    def setup_dbus_connection(self, Connection, bus_address_finder):
        if not Connection:
            Connection = DBusConnection
        if not bus_address_finder:
            bus_address_finder = pyomxplayerng.bus_finder.BusFinder()
        try:
            return Connection(bus_address_finder.get_address())
        except DBusConnectionError:
            connection = None
            if self.tries < 50:
                self.tries += 1
                time.sleep(0.05)
                return self.setup_dbus_connection(Connection, bus_address_finder)
            else:
                raise SystemError('DBus cannot connect to the OMXPlayer process')

    def can_quit(self):
        return bool(self._get_properties_interface().CanQuit())

    def fullscreen(self):
        return bool(self._get_properties_interface().FullScreen())

    def can_set_fullscreen(self):
        return bool(self._get_properties_interface().CanSetFullscreen())

    def has_track_list(self):
        return bool(self._get_properties_interface().HasTrackList())

    def identity(self):
        return str(self._get_properties_interface().Identity())

    def supported_uri_schemes(self):
        return map(str, self._get_properties_interface().SupportedUriSchemes())

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
        return self.duration_us() / (1000 * 1000)

    def _get_properties_interface(self):
        return self.connection.properties_interface
