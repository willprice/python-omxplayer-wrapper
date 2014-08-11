import subprocess

import dbus


class OMXPlayer(object):
    def __init__(self, filename, bus_address_finder=None):
        self._process = subprocess.Popen(['omxplayer', filename])
        self.bus = None
        if bus_address_finder is not None:
            self.bus = dbus.bus.BusConnection(bus_address_finder.get_address())
            proxy = self.bus.get_object('org.mpris.MediaPlayer2.omxplayer', '/org/mpris/MediaPlayer2')
            dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
            dbus.Interface(proxy, 'org.mpris.MediaPlayer2')
