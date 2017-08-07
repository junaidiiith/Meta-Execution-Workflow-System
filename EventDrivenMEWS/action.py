from uuid import uuid4


class Action:
    __slots__ =  ['id', '_task', '_description', 'event_conditions']

    def __init__(self,task=None):
        self.id = uuid4()
        self._description = 'finish ',task.name
        self._task = task
        self.event_conditions = set()

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
        data['description'] = self._description
        data['task'] = (self._task.id, self._task.name)
        ecs = []
        for ec in self.event_conditions:
            ecs.append(ec)
        data['event conditions'] = ecs
        return data
