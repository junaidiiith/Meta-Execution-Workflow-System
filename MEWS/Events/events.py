from task import Task
import events
import Conditions
import threading

class Events:

    def __init__(self, rid):
        self.task = self.get_task(rid) #instance of task
        # default condition task.status == "Completed" default task var = status
        self.condition = self.get_condition(rid) #instance of condition
        self.action = Events(self.get_action(rid))
        self.lock = threading.lock()

    def get_task(self,rid):
        return "task"

    def get_condition(self,rid):
        return "condition"

    def get_action(self,rid):
        return "action"

    def check_previous_events_completion(self):
        pass

    def get_value(self,condition,task):
        return True or False

    def check_condition(self):
        condition = self.get_value(self.condition,self.task)
        if condition:
            self.action.start()

    def start(self):
        self.check_previous_events_completion()
        with self.lock():
            self.task.status = "Started"
            self.task.execute()

        self.check_condition()