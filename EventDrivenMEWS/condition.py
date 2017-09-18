from uuid import uuid4


class Condition:
    __slots__ = ['id', '_description','_operator', '_operand', '_constant', 'event_id', 'type']

    def __init__(self, event_id, desc=None, type=None):
        self.id = str(uuid4())
        self.type = type
        self._description = str(desc)
        if not desc:
            self._operator = desc['operator']
            self._operand = desc['operand']
            self._constant = desc['constant']

        self.event_id = event_id

    @property
    def description(self):
        return self._description

    @property
    def operator(self):
        return self._operator

    @property
    def operand(self):
        return self._operand

    @property
    def constant(self):
        return self._constant

    def put(self):
        data = {}
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                data[attr] = self.attr
        return data


