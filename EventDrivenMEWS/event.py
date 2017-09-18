import uuid


class Event:
    __slots__ = ['id', '_task', '_description']

    def __init__(self, tsk):
        # self.id = tsk.id
        self._task = tsk
        if tsk:
            self._description = 'start ', tsk.name

    @property
    def task(self):
        return self._task

    @property
    def description(self):
        return self._description

    def set_task(self, task):
        self._task = task
        self.set_description("start "+task.name)

    def set_description(self, desc):
        self._description = desc

    def put(self):
        data = dict()
        data['id'] = self.id
        data['task'] = (self._task.id, self._task.name)
        data['description'] = self._description
        return data