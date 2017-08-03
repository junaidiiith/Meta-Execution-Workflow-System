from uuid import uuid4


class Action:
    __slots__ =  ['id', '_task', '_description', 'event_conditions']

    def __init__(self,task):
        self.id = uuid4()
        self._description = 'start ',task.name
        self._task = task
        self.event_conditions = set()

    @property
    def task(self):
        return self._task

    @property
    def description(self):
        return self._description
