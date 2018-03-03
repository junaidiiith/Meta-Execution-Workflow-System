from .dispatcher import EventDispatcher
from .event import Event
from .event_queue import EventQueue
from .workflow import Workflow
from EventDrivenMEWS.mongo_database import Database as Db


class Executor(object):
    def __init__(self, meta_workflow, user_workflow):
        self._meta_workflow = Workflow(meta_workflow)
        self._user_workflow = Workflow(user_workflow)
        self.meta_dispatcher = EventDispatcher()
        self.user_dispatcher = EventDispatcher()
        self.register_events(self.meta_dispatcher, meta_workflow)
        self.register_events(self.user_dispatcher, user_workflow)
        self.meta_event_q = EventQueue(self.meta_workflow.start)
        self.user_event_q = EventQueue(self.user_workflow.start)

    def register_events(self, dispatcher, workflow_id):
        events = Db().find_many_records("Events", {'workflow_id': workflow_id})
        for event in events:
            rules = event['rules']
            for rule in rules:
                dispatcher.add_event_listener(event['name'], rule)

    def execute(self):
        while self.meta_event_q.current_event:
            event = self.meta_event_q.current_event()
            raised_events = self.meta_dispatcher.\
                dispatch_event(event, self.user_event_q, self.user_dispatcher, self.user_workflow)
            for event in raised_events:
                self.meta_event_q.push(Event(event))
            self.meta_event_q.pop()

    @property
    def user_workflow(self):
        return self._user_workflow

    @property
    def meta_workflow(self):
        return self._meta_workflow
