from actionhandler import ActionHandler
from states import TaskStates

class EventHandler:
    def __init__(self):
        self.actions = {}
        self.actionhandler = ActionHandler(self)

    def add_event(self,event):
        self.actions[event] = {}

    def get_action(self,event):
        return self.actions[event]

    def register_action(self,event,action,callback=None):
        if callback is None:
            callback = getattr(self.actionhandler,'execute')
        self.get_action(event)[action] = callback

    def remove_action(self,event):
        del self.actions[event]

    def fire(self,event,*args,**kwargs):
        event.task.state = TaskStates.READY
        for action,callback in self.get_action(event):
            callback(action, *args,**kwargs)
