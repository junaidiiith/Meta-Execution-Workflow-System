from eventhandler import EventHandler
from database_funcs import Database

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

    def get_start_event(self,w):
        events = self.dbs.find_many_records("Events",{"workflow_id":w.id})
        for event in events:
            if event.task_id.lower() == "start":
                return event
        return None

    def execute(self):
        me = self.mEHandler.actions.keys()  #Add queues here in place of me
        while len(me):
            for eve in me:
                task = self.dbs.find_one_record("Tasks",{"name":eve.task_id, "workflow_id":self.mw.id})
                self.mEHandler.register_action(eve, task.action, task.handler)
                self.mEHandler.fire(eve,ueh=self.uEHandler, uw = self.uw )
            me = self.mEHandler.actions.keys()