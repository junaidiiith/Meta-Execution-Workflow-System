import uuid


class Event:
    __slots__ = ['id', '_task', '_description']

    def __init__(self, tsk):
        self.id = uuid.uuid4()
        self._task = tsk
        self._description = "start ",tsk.name

    @property
    def task(self):
        return self._task