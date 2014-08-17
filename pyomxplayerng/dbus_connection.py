import dbus


class DBusConnection(object):
    """
    Attributes:
    proxy       The proxy object by which one interacts with a dbus object,
                this makes communicating with a similar to that of communicating
                with a  POJO.
    """

    def __init__(self, bus_address):
        self._address = bus_address
        self._bus = self._create_connection()
        self.proxy = self._get_proxy()
        self._create_media_interfaces_on_proxy(self.proxy)

    def _create_connection(self):
        return dbus.bus.BusConnection(self._address)

    def _get_proxy(self):
        return self._bus.get_object('org.mpris.MediaPlayer2.omxplayer', '/org/mpris/MediaPlayer2')

    def _create_media_interfaces_on_proxy(self, proxy):
        self._interface(proxy, 'org.freedesktop.DBus.Properties')
        self._interface(proxy, 'org.mpris.MediaPlayer2')

    def _interface(self, proxy, interface):
        dbus.Interface(proxy, interface)