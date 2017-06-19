from uuid import uuid4

from task import Task
import json
from workflow import Workflow
# import logging
# LOG = logging.getLogger(__name__)


class Executor:
    def __init__(self,ew,sw):
        assert ew is not None
        assert sw is not None
        self.ew = Workflow(ew)
        self.sw = Workflow(sw)
        self.ew_tasks = [self.ew.start]
        self.sw_tasks = []
        self.ew_state = 'FUTURE'
        self.exec_id = uuid4()
        self.wfs = (self.ew.id,self.sw.id)
        self.log = []
        self.update_db()

    def update_db(self):
        pass

    def execute(self):

        for task in self.ew_tasks:
            ewt,swt = task.execute(sw=self.sw,sw_tasks = self.sw_tasks)
            self.sw_tasks.append(swt)
            self.ew_tasks.append(ewt)
