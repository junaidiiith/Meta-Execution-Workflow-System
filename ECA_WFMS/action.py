class Action(object):
    def __init__(self, name, handler, raised_events):
        self._name = name
        self._handler = handler
        self._raised_events = raised_events

    @property
    def name(self):
        return self._name

    @property
    def handler(self):
        return self._handler

    @property
    def raised_events(self):
        return self._raised_events
