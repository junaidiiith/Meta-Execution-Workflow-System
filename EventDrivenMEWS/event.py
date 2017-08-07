import uuid


class Event:
    __slots__ = ['id', '_task', '_description']

    def __init__(self, tsk=None):
        self.id = uuid.uuid4()
        self._task = tsk
        self._description = "start ",tsk.name

    @property
    def task(self):
        return self._task

    @property
    def description(self):
        return self._description

    def set_task(self, task):
        self._task = task

    def put(self):
        data = dict()
        data['id'] = self.id
        data['task'] = (self._task.id, self._task.name)
        data['description'] = self._description
        return data