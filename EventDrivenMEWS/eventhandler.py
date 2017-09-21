from actionhandler import ActionHandler
from states import TaskStates
from copy import copy

from database_funcs import Database

class EventHandler:
    def __init__(self):
        self.waiting_queue = []
        self.ready_queue = []
        self.dbs = Database()
        self.type = type(self.dbs.find_one_record("Events", {})['_id'])
        self.actionhandler = ActionHandler(self)

    def add_event(self,event):
        # t = type(event['_id'])
        print("Adding event", event["Description"])
        self.waiting_queue.append(event['_id'])
    # def get_action(self,event):
    #     print(self.actions)
    #     return self.actions[event['_id']]

    def remove_event(self, event):
        self.waiting_queue.remove(event['_id'])

    def register_action(self,action):
        # print(type(event))
        # print("value",self.actions[event])

        # if callback is None:
        #     callback = getattr(self.actionhandler,'execute')
        # self.dbs.add_to_database("ActionHandler",{"event":event['_id'], "workflow_id":self.workflow_id, "callback":callback })
        self.ready_queue.append(action['_id'])
        print("Registered")


    def update_task_state(self, act_or_eve, value):
        wid = act_or_eve['workflow_id']
        name = act_or_eve['task']
        task = self.dbs.find_one_record("Tasks", {"workflow_id": wid, 'name': name})
        temp = task
        task['state'] = value
        self.dbs.update_record("Tasks", temp, task)
        return task

    def fire(self,event_id,*args,**kwargs):
        event = self.dbs.find_one_record("Events",{'_id':event_id})
        print("Raising event for ", event['Description'], " finish")
        task = self.update_task_state(event, TaskStates.READY.value)

        # d = self.actions[event_id])
        # actions = self.dbs.find_many_records("ActionHandler",{"event":event['_id'], "workflow_id":self.workflow_id})

        while len(self.ready_queue):
            action = self.ready_queue.pop(0)
            print("Action is", action)
            callback = getattr(self.actionhandler,'execute')
            # print("kwargs:", kwargs)
            callback(action, *args,**kwargs)
            print("length q", len(self.ready_queue))

        # self.ready_queue = self.new_ready_queue
