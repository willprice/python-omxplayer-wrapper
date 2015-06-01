import subprocess
import time
import os
import signal
import logging
import threading

from functools import wraps
from glob import glob
from dbus import DBusException, Int64, ObjectPath

import omxplayer.bus_finder
from omxplayer.dbus_connection import DBusConnection, \
                                      DBusConnectionError

#### CONSTANTS ####
RETRY_DELAY = 0.05


#### FILE GLOBAL OBJECTS ####
logger = logging.getLogger(__name__)


#### CLASSES ####
class FileNotFoundError(Exception):
    pass

class FileCleaner(object):
    def __init__(self, path):
        self.path = path

    def clean(self):
        for file in glob(self.path):
            os.remove(file)

class OMXPlayer(object):
    """
    OMXPlayer controller

    This works by speaking to OMXPlayer over DBus sending messages.
    Args:
        filename (str): Path to the file you wish to play
    """
    def __init__(self, filename,
                 args=[], 
                 bus_address_finder=None, 
                 Connection=None,
                 cleaner=FileCleaner('/tmp/*omxplayer*')):
        logger.debug('Instantiating OMXPlayer')
        self.cleaner = cleaner
        self.clean_old_files()

        self.args = args

        if not bus_address_finder:
            bus_address_finder = omxplayer.bus_finder.BusFinder()
        if not Connection:
            Connection = DBusConnection

        self.tries = 0
        self._is_playing = True
        self._process = self.setup_omxplayer_process(filename)
        self.connection = self.setup_dbus_connection(Connection,
                                                     bus_address_finder)
        time.sleep(0.5)  # Wait for the DBus interface to be initialised
        self.pause()

    def clean_old_files(self):
        logger.debug("Removing old OMXPlayer pid files etc")
        self.cleaner.clean()

    def run_omxplayer(self, filename, devnull):
        def on_exit():
            logger.info("OMXPlayer process is dead, all DBus calls from here "
                        "will fail")

        def monitor(process, on_exit):
            process.wait()
            on_exit()

        command = ['omxplayer'] + self.args + [filename]
        logger.debug("Opening omxplayer with the command: %s" % command)
        process = subprocess.Popen(command,
                                   stdout=devnull,
                                   preexec_fn=os.setsid)
        m = threading.Thread(target=monitor, args=(process, on_exit))
        m.start()
        return process

    def setup_omxplayer_process(self, filename):
            logger.debug('Setting up OMXPlayer process')
            if not os.path.isfile(filename):
                raise FileNotFoundError("Could not find: {}".format(filename))
            with open(os.devnull, 'w') as devnull:
                process = self.run_omxplayer(filename, devnull)
                logger.debug('Process opened with PID %s' % process.pid)
                return process

    def setup_dbus_connection(self, Connection, bus_address_finder):
        logger.debug('Trying to connect to OMXPlayer via DBus')
        while self.tries < 50:
            logger.debug('DBus connect attempt: {}'.format(self.tries))
            try:
                connection = Connection(bus_address_finder.get_address())
                logger.debug(
                    'Connected to OMXPlayer at DBus address: %s' % connection)
                return connection

            except (DBusConnectionError, IOError):
                logger.debug('Failed to connect to OMXPlayer DBus address')
                self.tries += 1
                time.sleep(RETRY_DELAY)
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
        """
        Checks whether it is permissible to quit the OMXPlayer instance
        """
        return bool(self._get_root_interface().CanQuit())

    @check_player_is_active
    def fullscreen(self):
        """
        Checks whether the player can go fullscreen
        """
        return bool(self._get_root_interface().FullScreen())

    @check_player_is_active
    def can_set_fullscreen(self):
        """
        Checks whether the player can go fullscreen
        """
        return bool(self._get_root_interface().CanSetFullscreen())

    @check_player_is_active
    def has_track_list(self):
        """
        Checks whether the player has a tracklist
        (e.g. playlist or recently played items)
        Currently OMXPlayer doesn't have this functionality
        """
        return bool(self._get_root_interface().HasTrackList())

    @check_player_is_active
    def identity(self):
        """
        Checks whether the player has a tracklist
        (e.g. playlist or recently played items)
        Currently OMXPlayer doesn't have this functionality
        """
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
        """
        Returns:
            Current playback status (str):
            one of "Playing" | "Paused" | "Stopped"
        """
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
        return long(self._get_properties_interface().Position())

    @check_player_is_active
    def duration_us(self):
        return long(self._get_properties_interface().Duration())

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
        self._get_player_interface().Pause()

    @check_player_is_active
    def play_pause(self):
        self._get_player_interface().PlayPause()
        self._is_playing = not self._is_playing

    @check_player_is_active
    def stop(self):
        self._get_player_interface().Stop()

    @check_player_is_active
    def seek(self, relative_position_us):
        self._get_player_interface().Seek(Int64(relative_position_us))

    @check_player_is_active
    def set_position(self, position):
        self._get_player_interface().SetPosition(None, Int64(position*1000*1000))

    @check_player_is_active
    def list_video(self):
        return map(str, self._get_player_interface().ListVideo())

    @check_player_is_active
    def list_audio(self):
        return map(str, self._get_player_interface().ListAudio())

    @check_player_is_active
    def list_subtitles(self):
        return map(str, self._get_player_interface().ListSubtitles())

    @check_player_is_active
    def action(self, key):
        self._get_player_interface().Action(key)

    @check_player_is_active
    def is_playing(self):
        self._is_playing = (self.playback_status() == "Playing")
        logger.info("Playing?: %s" % self._is_playing)
        return self._is_playing

    @check_player_is_active
    def play_sync(self):
        self.play()
        logger.info("Playing synchronously")
        try:
            time.sleep(0.05)
            logger.debug("Wait for playing to start")
            while self.is_playing():
                time.sleep(0.05)
        except DBusException:
            logger.info(
                "Cannot play synchronously any longer as DBus calls time out."
            )

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
        logger.debug('Quitting OMXPlayer')
        try:
            os.killpg(self._process.pid, signal.SIGTERM)
            self._process.wait()
            logger.debug('SIGTERM Sent to pid: %s' % self._process.pid)
        except OSError:
            logger.debug('Could not find the process to kill')


#  MediaPlayer2.Player types:
#    Track_Id: DBus ID of track
#    Plaback_Rate: Multiplier for playback speed (1 = normal speed)
#    Volume: 0--1, 0 is muted and 1 is full volume
#    Time_In_Us: Time in microseconds
#    Playback_Status: Playing|Paused|Stopped
#    Loop_Status: None|Track|Playlist
