import subprocess
import time
import os
import signal
import logging
from functools import wraps

from dbus import DBusException


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import omxplayer.bus_finder
from omxplayer.dbus_connection import DBusConnection, DBusConnectionError


RETRY_DELAY = 0.05
OMXPLAYER_ARGS = ['--no-osd']

import threading


class OMXPlayer(object):
    def __init__(self, filename, bus_address_finder=None, Connection=None):
        logger.debug('Instantiating OMXPlayer')

        if not bus_address_finder:
            bus_address_finder = omxplayer.bus_finder.BusFinder()
        if not Connection:
            Connection = DBusConnection

        self.tries = 0
        self._is_playing = True
        self._process = self.setup_omxplayer_process(filename)
        self.connection = self.setup_dbus_connection(Connection, bus_address_finder)
        time.sleep(0.2)  # Wait for the DBus interface to be initialised
        self.pause()

    def run_omxplayer(self, devnull, filename):
        def on_exit():
            logger.info("OMXPlayer process is dead, all DBus calls from here "
                        "will fail")

        def monitor(process, on_exit):
            process.wait()
            on_exit()

        process = subprocess.Popen(
            ['omxplayer'] + OMXPLAYER_ARGS + [filename],
            stdout=devnull,
            preexec_fn=os.setsid)

        m = threading.Thread(target=monitor, args=(process, on_exit))
        m.start()
        return process

    def setup_omxplayer_process(self, filename):
        with open(os.devnull, 'w') as devnull:
            logger.debug('Setting up OMXPlayer process')
            process = self.run_omxplayer(devnull, filename)
            logger.debug('Process opened with PID %s' % process.pid)
            return process

    def setup_dbus_connection(self, Connection, bus_address_finder):
        logger.debug('Trying to connect to OMXPlayer via DBus')
        try:
            connection = Connection(bus_address_finder.get_address())
            logger.debug(
                'Connected to OMXPlayer at DBus address: %s' % connection)
            return connection

        except (DBusConnectionError, IOError):
            return self.handle_failed_dbus_connection(Connection, bus_address_finder)

    def handle_failed_dbus_connection(self, Connection, bus_address_finder):
        if self.tries < 50:
            logger.debug('DBus connect attempt: {}'.format(self.tries))
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
            logger.debug('Checking if process is still alive')
            if self._process.poll() is None:
                logger.debug('OMXPlayer is running, so execute %s' %
                             fn.__name__)
                return fn(self, *args, **kwargs)
            else:
                logger.info('Process is no longer alive, can\'t run command')

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
        self._is_playing = not self._is_playing
        self._get_player_interface().Pause()

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
        self._is_playing = self.playback_status() == "Playing"
        logger.info("Playing?: %s" % self._is_playing)
        return self._is_playing

    @check_player_is_active
    def play_sync(self):
        self.play()
        logger.info("Playing synchronously")
        try:
            time.sleep(0.05)
            while self.is_playing():
                time.sleep(0.05)
        except DBusException:
            logger.info("DBus timed out :(")

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
        logger.info('Quitting OMXPlayer')
        os.killpg(self._process.pid, signal.SIGTERM)
        logger.info('SIGTERM Sent to pid: %s' % self._process.pid)
        self._process.wait()
