from actionhandler import ActionHandler
from states import TaskStates


from database_funcs import Database

class EventHandler:
    def __init__(self):
        self.actions = {}
        self.dbs = Database()
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

    def update_task_state(self, act_or_eve, value):
        wid = act_or_eve['workflow_id']
        name = act_or_eve['task']
        task = self.dbs.find_one_record("Tasks", {"workflow_id": wid, 'name': name})
        temp = task
        task['state'] = value
        self.dbs.update_record("Tasks", temp, task)
        return task

    def fire(self,event,*args,**kwargs):
        task = self.update_task_state(event, TaskStates.READY.value)

        for action,callback in self.get_action(event):
            callback(action, *args,**kwargs)
