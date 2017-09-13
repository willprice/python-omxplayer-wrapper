import subprocess
import time
import os
import signal
import logging
import threading
import math
import sys
try: # python2
    from urlparse import urlsplit
except ImportError: # python3
    from urllib.parse import urlsplit

if sys.version_info > (3,):
    long = int

from decorator import decorator
from dbus import DBusException, Int64, String, ObjectPath
import dbus.types

from omxplayer.bus_finder import BusFinder
from omxplayer.dbus_connection import DBusConnection, \
                                      DBusConnectionError

from evento import Event

#### CONSTANTS ####
RETRY_DELAY = 0.05


#### FILE GLOBAL OBJECTS ####
logger = logging.getLogger(__name__)



def _check_player_is_active(fn):
    # wraps is a decorator that improves debugging wrapped methods
    def wrapped(fn, self, *args, **kwargs):
        logger.debug('Checking if process is still alive')
        # poll determines whether the process has terminated,
        # if it hasn't it returns None.
        if self._process.poll() is None:
            logger.debug('OMXPlayer is running, so execute %s' %
                            fn.__name__)
            return fn(self, *args, **kwargs)
        else:
            raise OMXPlayerDeadError('Process is no longer alive, can\'t run command')

    return decorator(wrapped, fn)

def _from_dbus_type(fn):
    def wrapped(fn, self, *args, **kwargs):
            return from_dbus_type(fn(self, *args, **kwargs))

    return decorator(wrapped, fn)

#### CLASSES ####
class FileNotFoundError(Exception):
    pass


class OMXPlayerDeadError(Exception):
    pass


class OMXPlayer(object):
    """
    OMXPlayer controller

    This works by speaking to OMXPlayer over DBus sending messages.

    Args:
        source (str): Path to the file (as ~/Videos/my-video.mp4) or URL you wish to play
        args (list): used to pass option parameters to omxplayer.  see: https://github.com/popcornmix/omxplayer#synopsis


    Multiple argument example:

    >>> OMXPlayer('path.mp4', args=['--no-osd', '--no-keys', '-b'])

    """
    def __init__(self, source,
                 args=[],
                 bus_address_finder=None,
                 Connection=None,
                 dbus_name=None,
                 pause=False):
        logger.debug('Instantiating OMXPlayer')

        self.args = args
        self._is_playing = True
        self._source = source
        self._dbus_name = dbus_name
        self._Connection = Connection if Connection else DBusConnection
        self._bus_address_finder = bus_address_finder if bus_address_finder else BusFinder()

        #: Event called on pause ``callback(player)``
        self.pauseEvent = Event()
        #: Event called on play ``callback(player)``
        self.playEvent = Event()
        #: Event called on stop ``callback(player)``
        self.stopEvent = Event()
        #: Event called on seek ``callback(player, relative_position)``
        self.seekEvent = Event()
        #: Event called on setting position ``callback(player, absolute_position)``
        self.positionEvent = Event()

        self._process = None
        self._connection = None
        self.load(source, pause=pause)

    def _load_source(self, source):
        if self._process:
            self.quit()

        self._process = self._setup_omxplayer_process(source)
        self._connection = self._setup_dbus_connection(self._Connection, self._bus_address_finder)

    def _run_omxplayer(self, source, devnull):
        def on_exit():
            logger.info("OMXPlayer process is dead, all DBus calls from here "
                        "will fail")

        def monitor(process, on_exit):
            process.wait()
            on_exit()

        command = ['omxplayer'] + self.args + [source]
        if self._dbus_name:
            command += ['--dbus_name', self._dbus_name]
        logger.debug("Opening omxplayer with the command: %s" % command)
        process = subprocess.Popen(command,
                                   stdin=devnull,
                                   stdout=devnull,
                                   preexec_fn=os.setsid)
        self._process_monitor = threading.Thread(target=monitor,
                                                 args=(process, on_exit))
        self._process_monitor.start()
        return process

    def _setup_omxplayer_process(self, source):
            logger.debug('Setting up OMXPlayer process')
            source_url = urlsplit(source)
            if not source_url.scheme and not os.path.isfile(source):
                raise FileNotFoundError("Could not find: {}".format(source))
            with open(os.devnull, 'w') as devnull:
                process = self._run_omxplayer(source, devnull)
                logger.debug('Process opened with PID %s' % process.pid)
                return process

    def _setup_dbus_connection(self, Connection, bus_address_finder):
        logger.debug('Trying to connect to OMXPlayer via DBus')
        tries = 0
        while tries < 50:
            logger.debug('DBus connect attempt: {}'.format(tries))
            try:
                connection = Connection(bus_address_finder.get_address(), self._dbus_name)
                logger.debug(
                    'Connected to OMXPlayer at DBus address: %s' % connection)
                return connection

            except (DBusConnectionError, IOError):
                logger.debug('Failed to connect to OMXPlayer DBus address')
                tries += 1
                time.sleep(RETRY_DELAY)
        raise SystemError('DBus cannot connect to the OMXPlayer process')

    """ Utilities """


    def load(self, source, pause=False):
        """
        Loads a new source (as a file) from ``source`` (a file path or URL)
        by killing the current ``omxplayer`` process and forking a new one.

        Args:
            source (string): Path to the file to play or URL
        """
        self._source = source
        self._load_source(source)
        if pause:
            time.sleep(0.5)  # Wait for the DBus interface to be initialised
            self.pause()

    """ ROOT INTERFACE PROPERTIES """

    @_check_player_is_active
    @_from_dbus_type
    def can_quit(self):
        """
        Returns:
            bool: whether the player can quit or not """
        return self._root_interface_property('CanQuit')

    @_check_player_is_active
    @_from_dbus_type
    def fullscreen(self):
        """
        Returns:
            bool: whether the player is fullscreen or not """
        return self._root_interface_property('Fullscreen')

    @_check_player_is_active
    @_from_dbus_type
    def can_set_fullscreen(self):
        """
        Returns:
            bool: whether the player can go fullscreen """
        return self._root_interface_property('CanSetFullscreen')

    @_check_player_is_active
    @_from_dbus_type
    def can_raise(self):
        """
        Returns:
            bool: whether the player can raise the display window atop of all other windows"""
        return self._root_interface_property('CanRaise')

    @_check_player_is_active
    @_from_dbus_type
    def has_track_list(self):
        """
        Returns:
            bool: whether the player has a track list or not"""
        return self._root_interface_property('HasTrackList')

    @_check_player_is_active
    @_from_dbus_type
    def identity(self):
        """
        Returns:
            str: 'omxplayer', the name of the player
        """
        return self._root_interface_property('Identity')

    @_check_player_is_active
    @_from_dbus_type
    def supported_uri_schemes(self):
        """
        Returns:
            str[]: list of supported URI schemes
        """
        return self._root_interface_property('SupportedUriSchemes')

    """ ROOT INTERFACE METHODS """

    """ PLAYER INTERFACE PROPERTIES """

    @_check_player_is_active
    @_from_dbus_type
    def can_go_next(self):
        """
        Returns:
            bool: Whether the player can move to the next item in the playlist
        """
        return self._player_interface_property('CanGoNext')

    @_check_player_is_active
    @_from_dbus_type
    def can_go_previous(self):
        """
        Returns:
            bool: Whether the player can move to the previous item in the
            playlist
        """
        return self._player_interface_property('CanGoPrevious')

    @_check_player_is_active
    @_from_dbus_type
    def can_seek(self):
        """
        Returns:
            bool: Whether the player can seek """
        return self._player_interface_property('CanSeek')

    @_check_player_is_active
    @_from_dbus_type
    def can_control(self):
        """
        Returns:
            bool: """
        return self._player_interface_property('CanControl')

    @_check_player_is_active
    @_from_dbus_type
    def can_play(self):
        """
        Returns:
            bool: """
        return self._player_interface_property('CanPlay')

    @_check_player_is_active
    @_from_dbus_type
    def can_pause(self):
        """
        Returns:
            bool: """
        return self._player_interface_property('CanPause')

    @_check_player_is_active
    @_from_dbus_type
    def playback_status(self):
        """
        Returns:
            str: One of ("Playing" | "Paused" | "Stopped")
        """
        return self._player_interface_property('PlaybackStatus')

    @_check_player_is_active
    @_from_dbus_type
    def volume(self):
        """
        Returns:
            float: Volume in millibels
        """
        vol = self._player_interface_property('Volume')
        return 2000 * math.log(vol, 10)

    @_check_player_is_active
    @_from_dbus_type
    def set_volume(self, volume):
        """
        Args:
            float: Volume in millibels
        """
        return self._player_interface_property('Volume', dbus.Double(10**(volume/2000.0)))

    @_check_player_is_active
    @_from_dbus_type
    def _position_us(self):
        """
        Returns:
            int: position in microseconds
        """
        return self._player_interface_property('Position')

    def position(self):
        """
        Returns:
            int: position in seconds
        """
        return self._position_us() / (1000.0 * 1000.0)

    @_check_player_is_active
    @_from_dbus_type
    def minimum_rate(self):
        """
        Returns:
            float: minimum playback rate (as proportion of normal rate)
        """
        return self._player_interface_property('MinimumRate')

    @_check_player_is_active
    @_from_dbus_type
    def maximum_rate(self):
        """
        Returns:
            float: maximum playback rate (as proportion of normal rate)
        """
        return self._player_interface_property('MaximumRate')

    @_check_player_is_active
    @_from_dbus_type
    def rate(self):
        """
        Returns:
            float: playback rate
        """
        return self._player_interface_property('MaximumRate')

    @_check_player_is_active
    @_from_dbus_type
    def set_rate(self, rate):
        """
        Set the playback rate of the video as a multiple of the default playback speed

        e.g. `player.set_rate(2)` will play twice as fast and `player.set_rate(0.5)`
             will play half speed.
        Returns:
            None:
        """
        return self._player_interface_property('Rate', dbus.Double(rate))

    @_check_player_is_active
    @_from_dbus_type
    def metadata(self):
        """
        Returns
            dict: containing track information ('URI', 'length')
        """
        return self._player_interface_property('Metadata')

    """ PLAYER INTERFACE NON-STANDARD PROPERTIES """

    @_check_player_is_active
    @_from_dbus_type
    def aspect_ratio(self):
        """
        Returns
            float: aspect ratio
        """
        return self._player_interface_property('Aspect')

    @_check_player_is_active
    @_from_dbus_type
    def video_stream_count(self):
        """
        Returns
            int: number of video streams
        """
        return self._player_interface_property('VideoStreamCount')

    @_check_player_is_active
    @_from_dbus_type
    def width(self):
        """
        Returns
            int: video width in px
        """
        return self._player_interface_property('ResWidth')

    @_check_player_is_active
    @_from_dbus_type
    def height(self):
        """
        Returns
            int: video height in px
        """
        return self._player_interface_property('ResHeight')

    @_check_player_is_active
    @_from_dbus_type
    def _duration_us(self):
        """
        Returns
            int: total length in microseconds
        """
        return self._player_interface_property('Duration')

    @_check_player_is_active
    def duration(self):
        """
        Returns:
            float: The duration in seconds
        """
        return self._duration_us() / (1000.0 * 1000.0)


    """ PLAYER INTERFACE METHODS """

    @_check_player_is_active
    def pause(self):
        """
        Return:
            None:
        """
        self._player_interface.Pause()
        self._is_playing = False
        self.pauseEvent(self)

    @_check_player_is_active
    def play_pause(self):
        """
        Return:
            None:
        """
        self._player_interface.PlayPause()
        self._is_playing = not self._is_playing
        if self._is_playing:
            self.playEvent(self)
        else:
            self.pauseEvent(self)

    @_check_player_is_active
    @_from_dbus_type
    def stop(self):
        self._player_interface.Stop()
        self.stopEvent(self)

    @_check_player_is_active
    @_from_dbus_type
    def seek(self, relative_position):
        """
        Args:
            relative_position (float): The position in seconds to seek to.
        """
        self._player_interface.Seek(Int64(1000.0 * 1000 * relative_position))
        self.seekEvent(self, relative_position)

    @_check_player_is_active
    @_from_dbus_type
    def set_position(self, position):
        """
        Args:
            position (float): The position in seconds.
        """
        self._player_interface.SetPosition(ObjectPath("/not/used"), Int64(position * 1000.0 * 1000))
        self.positionEvent(self, position)

    @_check_player_is_active
    @_from_dbus_type
    def set_alpha(self, alpha):
        """
        Args:
            alpha (float): The transparency (0..255)
        """
        self._player_interface.SetAlpha(ObjectPath('/not/used'), Int64(alpha))

    @_check_player_is_active
    def mute(self):
        """
        Turns mute on, if the audio is already muted, then this does not do
        anything

        Returns:
            None:
        """
        self._player_interface.Mute()

    @_check_player_is_active
    def unmute(self):
        """
        Unmutes the video, if the audio is already unmuted, then this does
        not do anything

        Returns:
            None:
        """
        self._player_interface.Unmute()


    @_check_player_is_active
    @_from_dbus_type
    def set_aspect_mode(self, mode):
        """
        Args:
            mode (str): One of ("letterbox" | "fill" | "stretch")
        """
        self._player_interface.SetAspectMode(ObjectPath('/not/used'), String(mode))

    @_check_player_is_active
    @_from_dbus_type
    def set_video_pos(self, x1, y1, x2, y2):
        """
        Args:
            Image position (int, int, int, int):
        """
        position = "%s %s %s %s" % (str(x1),str(y1),str(x2),str(y2))
        self._player_interface.VideoPos(ObjectPath('/not/used'), String(position))

    @_check_player_is_active
    def video_pos(self):
        """
        Returns:
        """
        position_string = self._player_interface.VideoPos(ObjectPath('/not/used'), String(position))
        return list(map(int, position_string.split(" ")))

    @_check_player_is_active
    @_from_dbus_type
    def set_video_crop(self, x1, y1, x2, y2):
        """
        Args:
            Image position (int, int, int, int):
        """
        crop = "%s %s %s %s" % (str(x1),str(y1),str(x2),str(y2))
        self._player_interface.SetVideoCropPos(ObjectPath('/not/used'), String(crop))

    @_check_player_is_active
    def hide_video(self):
        """
        TODO
        """
        self._player_interface.HideVideo()

    @_check_player_is_active
    def show_video(self):
        """
        TODO
        """
        self._player_interface.UnHideVideo()

    @_check_player_is_active
    @_from_dbus_type
    def list_audio(self):
        """
        Returns:
            [str]: A list of all known audio streams, each item is in the
            format: ``<index>:<language>:<name>:<codec>:<active>``
        """
        return self._player_interface.ListAudio()

    @_check_player_is_active
    @_from_dbus_type
    def list_video(self):
        """
        Returns:
            [str]: A list of all known video streams, each item is in the
            format: ``<index>:<language>:<name>:<codec>:<active>``
        """
        return self._player_interface.ListVideo()


    @_check_player_is_active
    @_from_dbus_type
    def list_subtitles(self):
        """
        Returns:
            [str]: A list of all known subtitles, each item is in the
            format: ``<index>:<language>:<name>:<codec>:<active>``
        """
        return self._player_interface.ListSubtitles()

    @_check_player_is_active
    def select_subtitle(self, index):
        """
        TODO
        """
        return self._player_interface.SelectSubtitle(dbus.Int32(index))

    @_check_player_is_active
    def select_audio(self, index):
        """
        TODO
        """
        return self._player_interface.SelectAudio(dbus.Int32(index))

    @_check_player_is_active
    def show_subtitles(self):
        """
        TODO
        """
        return self._player_interface.ShowSubtitles()

    @_check_player_is_active
    def hide_subtitles(self):
        """
        TODO
        """
        return self._player_interface.HideSubtitles()

    @_check_player_is_active
    @_from_dbus_type
    def action(self, code):
        """
        Executes a keyboard command via a code

        Args:
            code (int): The key code you wish to emulate
                        refer to ``keys.py`` for the possible keys

        Returns:
            None:
        """
        self._player_interface.Action(code)

    @_check_player_is_active
    @_from_dbus_type
    def is_playing(self):
        """
        Returns:
            bool: Whether the player is playing
        """
        self._is_playing = (self.playback_status() == "Playing")
        logger.info("Playing?: %s" % self._is_playing)
        return self._is_playing

    @_check_player_is_active
    @_from_dbus_type
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
    @_from_dbus_type
    def play(self):
        """
        Returns:
            None:
        """
        if not self.is_playing():
            self.play_pause()
            self._is_playing = True
            self.playEvent(self)

    @_check_player_is_active
    @_from_dbus_type
    def next(self):
        """
        TODO
        """
        return self._player_interface.Next()

    @_check_player_is_active
    @_from_dbus_type
    def previous(self):
        """
        TODO
        """
        return self._player_interface.Previous()

    @property
    def _root_interface(self):
        return self._connection.root_interface

    @property
    def _player_interface(self):
        return self._connection.player_interface

    @property
    def _properties_interface(self):
        return self._connection.properties_interface

    def _interface_property(self, interface, prop, val):
        if val:
            return self._properties_interface.Set(interface, prop, val)
        else:
            return self._properties_interface.Get(interface, prop)

    def _root_interface_property(self, prop, val=None):
        return self._interface_property(self._root_interface.dbus_interface, prop, val)

    def _player_interface_property(self, prop, val=None):
        return self._interface_property(self._player_interface.dbus_interface, prop, val)

    def quit(self):
        try:
            logger.debug('Quitting OMXPlayer')
            process_group_id = os.getpgid(self._process.pid)
            os.killpg(process_group_id, signal.SIGTERM)
            logger.debug('SIGTERM Sent to pid: %s' % process_group_id)
            self._process_monitor.join()
        except OSError:
            logger.error('Could not find the process to kill')

        self._process = None

        self._process = None

    @_check_player_is_active
    @_from_dbus_type
    def get_source(self):
        """
        Returns:
            str: source currently playing
        """
        return self._source

    # For backward compatibility
    @_check_player_is_active
    @_from_dbus_type
    def get_filename(self):
        """
        Returns:
            str: source currently playing

        .. deprecated:: 0.2.0
           Use: :func:`get_source` instead.
        """
        return self.get_source()


def from_dbus_type(dbusVal):
    def from_dbus_dict(dbusDict):
        d = dict()
        for dbusKey, dbusVal in dbusDict.items():
            d[from_dbus_type(dbusKey)] = from_dbus_type(dbusVal)
        return d

    typeUnwrapper = {
        dbus.types.Dictionary: from_dbus_dict,
        dbus.types.Array: lambda x: list(map(from_dbus_type, x)),
        dbus.types.Double: float,
        dbus.types.Boolean: bool,
        dbus.types.Byte: int,
        dbus.types.Int16: int,
        dbus.types.Int32: int,
        dbus.types.UInt32: int,
        dbus.types.Int64: int,
        dbus.types.UInt32: int,
        dbus.types.UInt64: int,
        dbus.types.ByteArray: str,
        dbus.types.ObjectPath: str,
        dbus.types.Signature: str,
        dbus.types.String: str
    }
    try:
        return typeUnwrapper[type(dbusVal)](dbusVal)
    except KeyError:
        return dbusVal

#  MediaPlayer2.Player types:
#    Track_Id: DBus ID of track
#    Plaback_Rate: Multiplier for playback speed (1 = normal speed)
#    Volume: 0--1, 0 is muted and 1 is full volume
#    Time_In_Us: Time in microseconds
#    Playback_Status: Playing|Paused|Stopped
#    Loop_Status: None|Track|Playlist
