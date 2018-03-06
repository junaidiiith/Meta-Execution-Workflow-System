from .dispatcher import EventDispatcher
from .event import Event
from .event_queue import EventQueue
from .mongo_database import Database as Db


class Executor(object):
    def __init__(self, meta_workflow, user_workflow):
        self._meta_workflow = meta_workflow
        self._user_workflow = user_workflow
        self.meta_dispatcher = EventDispatcher()
        self.user_dispatcher = EventDispatcher()
        self.meta_event_q = EventQueue(self.meta_workflow.start)
        self.user_event_q = EventQueue(self.user_workflow.start)

        register_events(self.meta_dispatcher, self.meta_workflow)
        register_events(self.user_dispatcher, self.user_workflow)

        init_data(self.meta_workflow)
        init_data(self.user_workflow)

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


def init_data(workflow):
    tasks = Db().find_many_records("Tasks", {'workflow_id': workflow.id})
    data = dict()
    data['global'] = Db().find_one_record("Globals", {'workflow_id': workflow.id})['globals']
    data['local'] = dict()
    l = list()
    for task in tasks:
        for obj in task['input_params'] + task['output_params']:
            d = dict()
            d['task_name'] = task['name']
            d['name'] = obj
            d['value'] = None
            l.append(d)
        d = dict()
        d['task_name'] = task['name']
        d['name'] = 'state'
        d['value'] = 'not started'
        l.append(d)
    data['local'] = l
    Db().add_to_database("Exec_data", {'workflow_id': workflow.id, 'data': data})


def register_events(dispatcher, workflow):
    events = Db().find_many_records("Events", {'workflow_id': workflow.id})
    for event in events:
        rules = event['rules']
        for rule in rules:
            dispatcher.add_event_listener(event['name'], rule)
