from database_funcs import Database
db = Database()
from states import TaskStates
import sys
typ = type(db.find_one_record("Events",{})['_id'])

class Tasks:
    def __init__(self, *args, **kwargs):
        self.type = 'meta'
        self.uEHandler = kwargs['ueh']
        self.uw = kwargs['uw']

    def start(self,*args,**kwargs):
        # print("Arguments are", args)
        print("Starting workflow tasks")
        kwargs['state'] = TaskStates.STARTED.value
        return kwargs

    def create_workflow_instance(self,*args, **kwargs):
        # print("Arguments are", args)
        print("Creating workflow instance")
        kwargs['state'] = TaskStates.RUNNING.value
        return kwargs

    def get_a_task(self,*args,**kwargs):
        print("Getting an event for the next task")
        print("Arguments are", args)
        if len(self.uEHandler.waiting_queue):
            # print("returning", self.uEHandler.waiting_queue[-1])
            kwargs['output'] = True
        else:
            kwargs['output'] = False
        return  kwargs
        # return  self.uEHandler.waiting_queue[0]


    def check_resources(self,*args,**kwargs):
        # print("Arguments", args)
        if len(self.uEHandler.waiting_queue):
            print("Check resources")
            event = self.uEHandler.waiting_queue[-1]
            kwargs['output'] = "available"
            return kwargs
        # for
        # for event in self.uEHandler.actions.keys():
        #     if not event.task.handler:
        #         return False
        # return True
    def check_task(self, *args, **kwargs):
        print("Arguments", args)
        print("Checking next task!")
        if len(self.uEHandler.waiting_queue):
            event = self.uEHandler.waiting_queue[-1]
            task = db.find_one_record("Tasks",{"event":event})
            value = task['name'].lower() == "end"
            print("Returning from check task", not value)
            kwargs['output'] = not value
            return kwargs
        kwargs['output'] = False
        print("Returning", kwargs)
        return kwargs

    def end(self, *args, **kwargs):
        print("Ending task of the workflow")
        kwargs['state'] = TaskStates.FINISHED.value
        return kwargs
        # sys.exit(0)

    def update_task_state(self, act_or_eve, value):
        # print("Updating task state to ", value)
        wid = act_or_eve['workflow_id']
        name = act_or_eve['task']
        db.update_record("Data",{"workflow_id":wid,"task_id":name, "type":"local", "variable":"state"},{"value":value.lower()})
        task = db.find_one_record("Tasks", {"workflow_id": wid, 'name': name})
        return task

    def execute(self,*args,**kwargs):

        print("Executing execute function")

        eve = self.uEHandler.waiting_queue.pop(0)
        id = typ(eve)
        event = db.find_one_record("Events",{'_id':id})
        print("Registering ", event['Description'])
        task = db.find_one_record("Tasks", {"name": event['task'], "workflow_id": self.uw})
        action = db.find_one_record("Actions",{'_id':task['action']})
        self.uEHandler.register_action(action)

        print("Raising events!")
        id = typ(eve)
        event = db.find_one_record("Events", {'_id': id})
        print("Raising ",event['Description'])
        self.uEHandler.fire(event['_id'])
        print("---------------------Execution of user task done--------------------------------------------------------")
        # print("length is",len(self.uEHandler.waiting_queue))
