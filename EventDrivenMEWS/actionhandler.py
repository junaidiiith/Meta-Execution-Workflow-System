from eventhandler import EventHandler
from states import TaskStates

class ActionHandler:
    def __init__(self):
        self.events = {}

    def get_events(self,action):
        return self.events[action]

    def register_event(self,action, event, callback=None):
        if not callback:
            callback = getattr(EventHandler,'add_event')
        self.get_events(action)[event] = callback

    def remove_event(self,action,event):
        del self.events[action][event]

    def get_rule(self,event):
        #get rule from db with event_id = event.id
        return "rule"

    def add_to_worklist(self,task):
        #add task to the worklist of the owner of the task
        pass

    def execute(self,action,callback,*args, **kwargs):

        self.action = action
        task = self.action.task
        self.add_to_worklist(task)
        task.state = TaskStates.READY
        # code to execute the action i.e handler of action.task
        ##
        data = callback(*args,**kwargs)

        # for k,v in data:
        #     self.action.task.data[k] = v    #Adding the output of the task to the task data dictionary
        self.action.task.data['output'] = data

        task.state = TaskStates.RUNNING
        ##
        ##
        task.state = TaskStates.FINISHED
        output_tasks = self.action.task.output_tasks
        for task in output_tasks:
            event = task.event
            rule = self.get_rule(event)
            if eval(rule.condition):
                self.register_event(self.action, event)
