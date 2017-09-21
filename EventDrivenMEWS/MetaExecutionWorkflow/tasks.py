from database_funcs import Database
db = Database()
import sys
typ = type(db.find_one_record("Events",{})['_id'])

class Tasks:
    def __init__(self, *args, **kwargs):
        self.type = 'meta'
        self.uEHandler = kwargs['ueh']
        self.uw = kwargs['uw']

    def start(self,*args,**kwargs):

        print("Starting workflow tasks")
        kwargs['state'] = "started"

    def create_workflow_instance(self,*args,**kwargs):
        print("Creating workflow instance")
        kwargs['state'] = "RUNNING"

    def get_a_task(self,*args,**kwargs):
        print("Getting an event for the next task")
        print("returning", self.uEHandler.waiting_queue[0])
        if len(self.uEHandler.waiting_queue):
            return True
        return False
        # return  self.uEHandler.waiting_queue[0]


    def check_resources(self,*args,**kwargs):
        print("Check resources")
        event = self.uEHandler.waiting_queue[0]
        task = db.find_one_record("Tasks", {"event": event})
        return "available"
        # for
        # for event in self.uEHandler.actions.keys():
        #     if not event.task.handler:
        #         return False
        # return True
    def check_task(self, *args, **kwargs):
        print("Checking next task!")
        event = self.uEHandler.waiting_queue[0]
        task = db.find_one_record("Tasks",{"event":event})
        value = task['name'].lower() == "end"
        print("Returning from check task", not value)
        return not value


    def end(self, *args, **kwargs):
        print("Ending task of the workflow")
        kwargs['state'] = "FINISHED"
        sys.exit(0)

    def execute(self,*args,**kwargs):

        print("Executing execute function")
        while len(self.uEHandler.waiting_queue):
            eve = self.uEHandler.waiting_queue.pop(0)
            id = typ(eve)
            event = db.find_one_record("Events",{'_id':id})
            # print("Registering ", event['Description'])
            task = db.find_one_record("Tasks", {"name": event['task'], "workflow_id": self.uw})
            action = db.find_one_record("Actions",{'_id':task['action']})
            self.uEHandler.register_action(action)

            print("Raising events!")
            id = typ(eve)
            event = db.find_one_record("Events", {'_id': id})
            print("Raising ",event['Description'])
            self.uEHandler.fire(event['_id'])
            print("length is",len(self.uEHandler.waiting_queue))
