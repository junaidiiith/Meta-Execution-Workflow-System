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
        # print("Adding start event to meta exec workflow")
        self.mEHandler.add_event(self.get_start_event(self.mw))
        self.uEHandler = EventHandler()
        # print("Adding start event to user workflow")
        self.uEHandler.add_event(self.get_start_event(self.uw))

    def get_start_event(self, w):
        event = self.dbs.find_one_record("Events", {"workflow_id": w, "task": "start"})
        if event:
            # print(event)
            self.dbs.add_to_database("Exec_data",{"workflow_id": w,
                                    "type": "local", "task": "start", "variable": "state", "value": "Not started"})
            globals = self.dbs.find_one_record("Workflow", {"id": w})['globals']
            for key, val in globals.items():
                record = {"workflow_id": w, "type": "global", "variable": key, "value": val}
                self.dbs.add_to_database("Exec_data", record)
                # print("Added ",self.dbs.find_one_record("Exec_data",record))
            return event
        print("Start event not found!")
        sys.exit(0)

    def get_event_from_id(self, id):
        typ = type(self.dbs.find_one_record("Events",{}))
        id = typ(id)
        return self.dbs.find_one_record("Events",{'_id':id})

    def execute(self):

        while len(self.mEHandler.waiting_queue):
            eve = self.mEHandler.waiting_queue.pop()
            id = self.type(eve)
            event = self.dbs.find_one_record("Events",{'_id':id})
            # print(event)
            # print("Raising ",event['Description'])
            task = self.dbs.find_one_record("Tasks", {"name": event['task'], "workflow_id": self.mw})
            action = self.dbs.find_one_record("Actions",{'_id':task['action']})
            # print("Registering action for ", action['Description'])
            self.mEHandler.register_action(action)
            self.mEHandler.fire(event['_id'], ueh=self.uEHandler, uw=self.uw)
            print("----Done with ", event['task'], "----")
