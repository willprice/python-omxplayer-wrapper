class BusFinder(object):
    def __init__(self, path='/tmp/omxplayerdbus'):
        self.path = path

    def get_address(self):
        with open(self.path, 'r') as f:
            self.address = f.read().strip()
        return self.address
