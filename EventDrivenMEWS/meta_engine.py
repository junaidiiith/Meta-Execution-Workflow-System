from eventhandler import EventHandler
from database_funcs import Database
import sys


class MetaEngine:
    # Output of a task is stored in the data dict of a task with key='output'
    def __init__(self, mw, uw):
        self.mw = mw
        self.uw = uw
        self.dbs = Database()
        self.type = type(self.dbs.find_one_record("Events",{})['_id'])

        self.mEHandler = EventHandler()
        self.mEHandler.add_event(self.get_start_event(self.mw))
        self.uEHandler = EventHandler()
        self.uEHandler.add_event(self.get_start_event(self.uw))

    def get_start_event(self, w):
        event = self.dbs.find_one_record("Events", {"workflow_id": w, "task": "start"})
        if event:
            # print(event)
            return event
        print("Start event not found!")
        sys.exit(0)

    def get_event_from_id(self, id):
        typ = type(self.dbs.find_one_record("Events",{}))
        id = typ(id)
        return self.dbs.find_one_record("Events",{'_id':id})

    def execute(self):

        waiting_queue = self.mEHandler.waiting_queue
        while len(waiting_queue):
            print("Registering events!")
            for eve in waiting_queue:
                id = self.type(eve)
                event = self.dbs.find_one_record("Events",{'_id':id})
                print("Registering ", event['Description'])
                task = self.dbs.find_one_record("Tasks", {"name": event['task'], "workflow_id": self.mw})
                action = self.dbs.find_one_record("Actions",{'_id':task['action']})
                # print(task)
                # print(type(event['_id']), type(task['action']))
                self.mEHandler.register_action(action)

            print("Raising events!")
            for eve in waiting_queue:
                id = self.type(eve)
                event = self.dbs.find_one_record("Events", {'_id': id})
                print("Raising ",event['Description'])
                self.mEHandler.fire(event['_id'], ueh=self.uEHandler, uw=self.uw)
            print("waiting queue",waiting_queue)
            waiting_queue = self.mEHandler.waiting_queue
