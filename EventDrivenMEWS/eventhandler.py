from actionhandler import ActionHandler
class EventHandler:
    def __init__(self, event):
        self.actions = {}

    def add_event(self,event):
        self.actions[event] = {}

    def get_action(self,event):
        return self.actions[event]

    def register_action(self,event,action,callback=None):
        if callback is None:
            callback = getattr(ActionHandler,'execute')
        self.get_action(event)[action] = callback

    def remove_action(self,event):
        del self.actions[event]

    def fire(self,event,*args,**kwargs):
        for action,callback in self.get_action(event):
            callback(*args,**kwargs)  #callback must have a keyword 'action' having the action as the parameter
