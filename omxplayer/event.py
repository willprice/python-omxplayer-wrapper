import logging
logger = logging.getLogger(__name__)

class Event:
    def __init__(self):
        self.handlers = set()
        self.counter = 0
        self.fireStack = 0
        self._handle_queue = []
        self._unhandle_queue = []

    def handle(self, handler):
        if self.isFiring():
            self._handle_queue.append(handler)
            return self

        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        if self.isFiring():
            self._unhandle_queue.append(handler)
            return self

        try:
            self.handlers.remove(handler)
        except:
            # raise ValueError("Handler is not handling this event, so cannot unhandle it.")
            logger.warning('Event.unhandle got unknown handler')
            # traceback.print_exc()
            # traceback.print_stack()

        return self

    def handles(self, handler):
        return handler in self.handlers

    def fire(self, *args, **kargs):
        # change state
        self.fireStack += 1

        # execute all handlers
        for handler in self.handlers:
            # the handler might have got 'unhandled' inside one of the
            # previous handlers
            if not handler in self._unhandle_queue:
                handler(*args, **kargs)

        # change state back
        self.fireStack -= 1

        # we're counting the number of fires (mostly for testing purposes)
        self.counter += 1

        # only if we're not still in a recursive fire situation
        if not self.isFiring():
            # process queues
            for handler in self._handle_queue:
                # add to our handlers list
                self.handle(handler)

            for handler in self._unhandle_queue:
                # remoev from our handlers list
                self.unhandle(handler)

            # reset queues
            self._handle_queue = []
            self._unhandle_queue = []

    def getHandlerCount(self):
        return len(self.handlers)

    def isFiring(self):
        return self.fireStack > 0

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount
    __contains__ = handles
