import subprocess
import time
import os
import signal
import logging
import threading
import math

from decorator import decorator
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
        args (list): used to pass option parameters to omxplayer.
        multiple argument example:
        # OMXPlayer('path.mp4', args=['--no-osd', '--no-keys', '-b'])
        info: https://github.com/popcornmix/omxplayer#synopsis
    """
    def __init__(self, filename,
                 args=[],
                 bus_address_finder=None,
                 Connection=None,
                 cleaner=FileCleaner('/tmp/*omxplayer*')):
        logger.debug('Instantiating OMXPlayer')
        self.cleaner = cleaner
        self._clean_old_files()

        self.args = args

        if not bus_address_finder:
            bus_address_finder = omxplayer.bus_finder.BusFinder()
        if not Connection:
            Connection = DBusConnection

        self.tries = 0
        self._is_playing = True
        self._filename = filename
        self._process = self._setup_omxplayer_process(filename)
        self.connection = self._setup_dbus_connection(Connection,
                                                     bus_address_finder)
        time.sleep(0.5)  # Wait for the DBus interface to be initialised
        self.pause()

    def _clean_old_files(self):
        logger.debug("Removing old OMXPlayer pid files etc")
        self.cleaner.clean()

    def _run_omxplayer(self, filename, devnull):
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
        self._process_monitor = threading.Thread(target=monitor, args=(process,
                                                               on_exit))
        self._process_monitor.start()
        return process

    def _setup_omxplayer_process(self, filename):
            logger.debug('Setting up OMXPlayer process')
            if not os.path.isfile(filename):
                raise FileNotFoundError("Could not find: {}".format(filename))
            with open(os.devnull, 'w') as devnull:
                process = self._run_omxplayer(filename, devnull)
                logger.debug('Process opened with PID %s' % process.pid)
                return process

    def _setup_dbus_connection(self, Connection, bus_address_finder):
        logger.debug('Trying to connect to OMXPlayer via DBus')
        while self.tries < 50:
            logger.debug('DBus connect attempt: {}'.format(self.tries))
            try:
                connection = Connection(bus_address_finder.get_address())
                self.dbus_pid = bus_address_finder.get_process()
                logger.debug(
                    'Connected to OMXPlayer at DBus address: %s' % connection)
                return connection

            except (DBusConnectionError, IOError):
                logger.debug('Failed to connect to OMXPlayer DBus address')
                self.tries += 1
                time.sleep(RETRY_DELAY)
        raise SystemError('DBus cannot connect to the OMXPlayer process')

    """ Utilities """

    def _check_player_is_active(fn):
        # wraps is a decorator that improves debugging wrapped methods
        def wrapped(fun, self, *args, **kwargs):
            logger.debug('Checking if process is still alive')
            # poll determines whether the process has terminated,
            # if it hasn't it returns None.
            if self._process.poll() is None:
                logger.debug('OMXPlayer is running, so execute %s' %
                             fn.__name__)
                return fn(self, *args, **kwargs)
            else:
                logger.info('Process is no longer alive, can\'t run command')

        return decorator(wrapped, fn)

    """ ROOT INTERFACE METHODS """

    @_check_player_is_active
    def can_quit(self):
        """
        Returns:
            bool: """
        return bool(self._get_root_interface().CanQuit())

    @_check_player_is_active
    def can_set_fullscreen(self):
        """
        Returns:
            bool: """
        return bool(self._get_root_interface().CanSetFullscreen())

    @_check_player_is_active
    def identity(self):
        """
        Get the ID of the media player

        Returns:
            bool:
        """
        return str(self._get_root_interface().Identity())

    """ PLAYER INTERFACE PROPERTIES """

    @_check_player_is_active
    def can_go_next(self):
        """
        Returns:
            bool: Whether the player can move to the next item in the playlist
        """
        return bool(self._get_properties_interface().CanGoNext())

    @_check_player_is_active
    def can_go_previous(self):
        """
        Returns:
            bool: Whether the player can move to the previous item in the
            playlist
        """
        return bool(self._get_properties_interface().CanGoPrevious())

    @_check_player_is_active
    def can_seek(self):
        """
        Returns:
            bool: Whether the player can seek """
        return bool(self._get_properties_interface().CanSeek())

    @_check_player_is_active
    def can_control(self):
        """
        Returns:
            bool: """
        return bool(self._get_properties_interface().CanControl())

    @_check_player_is_active
    def can_play(self):
        """
        Returns:
            bool: """
        return bool(self._get_properties_interface().CanPlay())

    @_check_player_is_active
    def can_pause(self):
        """
        Returns:
            bool: """
        return bool(self._get_properties_interface().CanPause())

    @_check_player_is_active
    def playback_status(self):
        """
        Returns:
            str: One of ("Playing" | "Paused" | "Stopped")
        """
        return str(self._get_properties_interface().PlaybackStatus())

    @_check_player_is_active
    def volume(self):
        """
        Returns:
            volume (float): Volume in millibels
        """
        vol = float(self._get_properties_interface().Volume())
        return 2000 * math.log(vol, 10)

    @_check_player_is_active
    def set_volume(self, volume):
        """
        Args:
            volume (float): Volume in millibels
        """
        return float(self._get_properties_interface().Volume(
            10**(volume/2000.0)
        ))

    @_check_player_is_active
    def mute(self):
        """
        Turns mute on, if the audio is already muted, then this does not do
        anything

        Returns:
            None:
        """
        self._get_properties_interface().Mute()

    @_check_player_is_active
    def unmute(self):
        """
        Unmutes the video, if the audio is already unmuted, then this does
        not do anything

        Returns:
            None:
        """
        self._get_properties_interface().Unmute()

    @_check_player_is_active
    def position(self):
        """
        Returns:
            float: The position in seconds
        """
        return self._get_properties_interface().Position() / (1000 * 1000.0)

    @_check_player_is_active
    def _duration_us(self):
        """
        Returns:
            long: The duration in microseconds
        """
        return long(self._get_properties_interface().Duration())

    @_check_player_is_active
    def duration(self):
        """
        Returns:
            float: The duration in seconds
        """
        return self._duration_us() / (1000 * 1000.0)

    @_check_player_is_active
    def minimum_rate(self):
        """
        Returns:
            str: The minimum playback rate
        """
        return float(self._get_properties_interface().MinimumRate())

    @_check_player_is_active
    def maximum_rate(self):
        """
        Returns:
            str: The maximum playback rate
        """
        return float(self._get_properties_interface().MaximumRate())

    """ PLAYER INTERFACE METHODS """
    @_check_player_is_active
    def pause(self):
        """
        Return:
            None:
        """
        self._get_player_interface().Pause()

    @_check_player_is_active
    def play_pause(self):
        """
        Return:
            None:
        """
        self._get_player_interface().PlayPause()
        self._is_playing = not self._is_playing

    @_check_player_is_active
    def stop(self):
        self._get_player_interface().Stop()

    @_check_player_is_active
    def seek(self, relative_position):
        """
        Args:
            relative_position (float): The position in seconds to seek to.
        """
        self._get_player_interface().Seek(Int64(relative_position))

    @_check_player_is_active
    def set_position(self, position):
        """
        Args:
            position (float): The position in seconds.
        """
        self._get_player_interface().SetPosition(ObjectPath("/not/used"), Int64(position*1000*1000))

    @_check_player_is_active
    def list_video(self):
        """
        Returns:
            [str]: A list of all known video streams, each item is in the
            format: ``<index>:<language>:<name>:<codec>:<active>``
        """
        return map(str, self._get_player_interface().ListVideo())

    @_check_player_is_active
    def list_audio(self):
        """
        Returns:
            [str]: A list of all known audio streams, each item is in the
            format: ``<index>:<language>:<name>:<codec>:<active>``
        """
        return map(str, self._get_player_interface().ListAudio())

    @_check_player_is_active
    def list_subtitles(self):
        """
        Returns:
            [str]: A list of all known subtitles, each item is in the
            format: ``<index>:<language>:<name>:<codec>:<active>``
        """
        return map(str, self._get_player_interface().ListSubtitles())

    @_check_player_is_active
    def action(self, code):
        """
        Executes a keyboard command via a code

        Args:
            code (int): The key code you wish to emulate
                        refer to ``keys.py`` for the possible keys

        Returns:
            None:
        """
        self._get_player_interface().Action(code)

    @_check_player_is_active
    def is_playing(self):
        """
        Returns:
            None:
        """
        self._is_playing = (self.playback_status() == "Playing")
        logger.info("Playing?: %s" % self._is_playing)
        return self._is_playing

    @_check_player_is_active
    def play_sync(self):
        """
        Returns:
            None:
        """
        self.play()
        logger.info("Playing synchronously")
        try:
            time.sleep(0.05)
            logger.debug("Wait for playing to start")
            while self.is_playing():
                time.sleep(0.05)
        except DBusException:
            logger.error(
                "Cannot play synchronously any longer as DBus calls timed out."
            )

    @_check_player_is_active
    def play(self):
        """
        Returns:
            None:
        """
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
            os.killpg(self._process.pid, signal.SIGINT)
            self._process.wait()
            self._process_monitor.join()
            logger.debug('SIGINT Sent to pid: %s' % self._process.pid)
        except OSError:
            logger.error('Could not find the process to kill')
        try:
            os.kill(int(self.dbus_pid), signal.SIGTERM)
        except OSError:
            logger.error('Could not find the Dbus process to kill')
        except:
            pass

    @_check_player_is_active
    def get_filename(self):
        """
        Returns:
            str: filename currently playing
        """
        return self._filename

    def __del__(self):
        self.quit()


#  MediaPlayer2.Player types:
#    Track_Id: DBus ID of track
#    Plaback_Rate: Multiplier for playback speed (1 = normal speed)
#    Volume: 0--1, 0 is muted and 1 is full volume
#    Time_In_Us: Time in microseconds
#    Playback_Status: Playing|Paused|Stopped
#    Loop_Status: None|Track|Playlist
