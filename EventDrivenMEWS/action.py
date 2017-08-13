from uuid import uuid4


class Action:
    __slots__ =  ['id', '_task', '_description', 'event_conditions']

    def __init__(self,tsk):
        self.id = tsk.id
        if tsk:
            self._description = 'finish ',tsk.name
        self._task = tsk
        self.event_conditions = list()

    @property
    def task(self):
        return self._task

    @property
    def description(self):
        return self._description

    def set_task(self, task):
        self._task = task
        self.set_description("finish "+task.name)

    def set_description(self, desc):
            self._description = desc

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
