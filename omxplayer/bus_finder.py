from logging import getLogger

logger = getLogger(__name__)


class BusFinder(object):
    def __init__(self, path='/tmp/omxplayerdbus'):
        self.path = path
        logger.debug('BusFinder initialised with path: %s' % path)

    def get_address(self):
        logger.debug('Opening file at %s' % self.path)
        with open(self.path, 'r') as f:
            logger.debug('Opened file at %s' % self.path)
            self.address = f.read().strip()
            logger.debug('Address \'%s\' parsed from file' % self.path)
        return self.address
