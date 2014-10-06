import os.path
import time
from logging import getLogger

logger = getLogger(__name__)


class BusFinder(object):
    def __init__(self, path='/tmp/omxplayerdbus.root'):
        self.path = path
        logger.debug('BusFinder initialised with path: %s' % path)

    def get_address(self):
        self.wait_for_file()
        logger.debug('Opening file at %s' % self.path)
        with open(self.path, 'r') as f:
            logger.debug('Opened file at %s' % self.path)
            self.address = f.read().strip()
            logger.debug('Address \'%s\' parsed from file' % self.path)
        return self.address

    def wait_for_file(self):
        while not os.path.isfile(self.path):
            time.sleep(0.05)