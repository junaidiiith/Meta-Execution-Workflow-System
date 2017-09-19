from eventhandler import EventHandler
from database_funcs import Database
import sys


class MetaEngine:
    # Output of a task is stored in the data dict of a task with key='output'
    def __init__(self, mw, uw):
        self.mw = mw
        self.uw = uw
        self.dbs = Database()

        self.mEHandler = EventHandler()
        self.mEHandler.add_event(self.get_start_event(self.mw))
        self.uEHandler = EventHandler()
        self.uEHandler.add_event(self.get_start_event(self.uw))

    def get_start_event(self, w):
        event = self.dbs.find_one_record("Events", {"workflow_id": w.id, "task": "start"})
        if event:
            return event
        print("Start event not found!")
        sys.exit(0)

    def execute(self):

        waiting_queue = self.mEHandler.actions.keys()
        while len(waiting_queue):
            print("Registering events!")
            for eve in waiting_queue:
                task = self.dbs.find_one_record("Tasks", {"name": eve.task, "workflow_id": self.mw.id})
                self.mEHandler.register_action(eve, task['action'])

            print("Raising events!")
            for eve in waiting_queue:
                self.mEHandler.fire(eve, ueh=self.uEHandler, uw=self.uw)
            waiting_queue = self.mEHandler.actions.keys()
