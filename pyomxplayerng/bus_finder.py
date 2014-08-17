class BusFinder(object):
    def __init__(self, path='/tmp/omxplayerdbus'):
        with open(path, 'r') as f:
            self.address = f.read().strip()

    def get_address(self):
        return self.address
