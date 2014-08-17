import dbus


class DBusConnectionError(Exception):
    """ Connection error raised when DBusConnection can't set up connection
    """
    pass

class DBusConnection(object):
    """
    Attributes:
    proxy                       The proxy object by which one interacts with a dbus object,
                                this makes communicating with a similar to that of communicating
                                with a  POJO.
    properties_interface        org.freedesktop.DBus.Properties interface proxy object
    mpris_interface             org.mpris.MediaPlayer2 interface proxy object
    """

    def __init__(self, bus_address):
        self._address = bus_address
        self._bus = self._create_connection()
        self.proxy = self._create_proxy()

    def _create_connection(self):
        return dbus.bus.BusConnection(self._address)

    def _create_proxy(self):
        try:
            proxy = self._bus.get_object('org.mpris.MediaPlayer2.omxplayer', '/org/mpris/MediaPlayer2')
            self._create_media_interfaces_on_proxy(proxy)
            return proxy
        except dbus.DBusException:
            raise DBusConnectionError('Could not get proxy object')

    def _create_media_interfaces_on_proxy(self, proxy):
        self.properties_interface = self._interface(proxy, 'org.freedesktop.DBus.Properties')
        self.mpris_interface = self._interface(proxy, 'org.mpris.MediaPlayer2')

    def _interface(self, proxy, interface):
        return dbus.Interface(proxy, interface)