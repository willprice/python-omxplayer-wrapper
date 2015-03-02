import os.path
import time
from glob import glob
from logging import getLogger

logger = getLogger(__name__)


class BusFinder(object):
    def __init__(self, path=None):
        self.path = path
        logger.debug('BusFinder initialised with path: %s' % path)

    def get_address(self):
        self.wait_for_file()
        logger.debug('Opening file at %s' % self.path)
        with open(self.path, 'r') as f:
            logger.debug('Opened file at %s' % self.path)
            self.address = f.read().strip()
            logger.debug('Address \'%s\' parsed from file' % self.address)
        return self.address

    def wait_for_file(self):
        if self.path:
            # Wait for the given path to exist.
            while not os.path.isfile(self.path):
                time.sleep(0.5)
        else:
            dbus_files = []

            # Wait for the files to exist.
            while not dbus_files:
                # Get a list of /tmp/omxplayerdbus.* files sorted by m-time.
                dbus_files = filter(lambda path: not path.endswith('.pid'),
                                    glob('/tmp/omxplayerdbus.*'))
                dbus_files.sort(key=lambda path: os.path.getmtime(path))
                time.sleep(0.5)

            # Pick the most recent /tmp/omxplayerdbus.* file.
            self.path = dbus_files[-1]

        # Once the file exists, wait until it has data.
        while not os.path.getsize(self.path):
            time.sleep(0.5)
