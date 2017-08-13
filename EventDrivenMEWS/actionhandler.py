from eventhandler import EventHandler
from states import TaskStates

class ActionHandler:
    def __init__(self,eh):
        self.eventhandler = eh
        self.events = {}

    def get_events(self,action):
        return self.events[action]

    def register_event(self,action, event, callback=None):
        if not callback:
            callback = getattr(self.eventhandler,'add_event')
        self.get_events(action)[event] = callback

    def remove_event(self,action,event):
        del self.events[action][event]

    def get_rule(self,event):
        #get rule from db with event_id = event.id
        return "rule"

    def add_to_worklist(self,task):
        #add task to the worklist of the owner of the task
        pass

    def evaluate(self,conditions):
        for condition in conditions:
            if not eval(condition):
                return False
        return True

    def execute(self,action,*args, **kwargs):

        self.action = action
        assert action.task is not None
        task = self.action.task
        self.add_to_worklist(task)
        task.state = TaskStates.READY
        mod,cls,func = task.handler
        cls = __import__(mod,cls)
        callback = getattr(cls,func)
        # code to execute the action i.e handler of action.task
        ##

        task.state = TaskStates.RUNNING
        ##
        ##
        task.data['output'] = callback(*args, **kwargs)
        task.state = TaskStates.FINISHED
        output_tasks = self.action.task.output_tasks
        for task in output_tasks:
            event = task.event
            rule = self.get_rule(event)
            if self.evaluate(rule.conditions):
                self.register_event(self.action, event)
