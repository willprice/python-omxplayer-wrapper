import subprocess

import pyomxplayerng.bus_finder
from pyomxplayerng.dbus_connection import DBusConnection


class OMXPlayer(object):
    def __init__(self, filename, bus_address_finder=None, connection=None):
        self._process = subprocess.Popen(['omxplayer', filename])
        if not connection:
            self.setup_dbus_connection(bus_address_finder)

    def setup_dbus_connection(self, bus_address_finder):
        if not bus_address_finder:
            bus_address_finder = pyomxplayerng.bus_finder.BusFinder()
        self.connection = DBusConnection(bus_address_finder.get_address())
