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
