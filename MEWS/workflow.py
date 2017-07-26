
import json
from uuid import uuid4

from task import Task


class Workflow:
    def __init__(self,wf,**kwargs):
        self.id = uuid4()
        data = json.load(wf)
        self.tasks = self.set_tasks(wf)
        self.description = data['description']
        self.file = data['file']
        self.type = data['type']
        self.start = Task(wf,"Start")

    def set_tasks(self,wf):
        tasks = json.load(wf)['task_specs']
        tsks = []
        for task in tasks.keys():
            tsks.append(Task(wf,task,workflow=self))
        return tsks