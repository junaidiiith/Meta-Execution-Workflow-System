class Event(object):
    def __init__(self, type=None, data=None):

        self._type = type
        self._data = data
        self.rule = None
        """Add description and other attributes"""

    @property
    def type(self):
        """
        Returns the event type
        """
        return self._type

    @property
    def data(self):
        """
        Returns the data associated to the event
        """
        return self._data

    def set_rule(self, rule):
        self.rule = rule

    def get_rule(self):
        return self.rule
