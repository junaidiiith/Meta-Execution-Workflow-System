from .mongo_database import Database
from .condition import Condition
db = Database()


class EventDispatcher(object):
    """
    Generic event dispatcher which listen and dispatch events
    """

    def __init__(self):
        self._events = dict()

    def __del__(self):
        """
        Remove all listener references at destruction time
        """
        self._events = None

    def has_listener(self, event_type, listener):
        """
        Return true if listener is register to event_type
        """
        # Check for event type and for the listener
        if event_type in self._events.keys():
            return listener in self._events[event_type]
        else:
            return False

    def my_import(self, name):
        __import__(name.rsplit('.', 1)[0])
        components = name.split('.')
        mod = __import__(components[0])
        # print(mod)
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    def run_handler(self, handler, *args, **kwargs):

        cls, func = self.my_import(handler[0]+'.'+handler[1])(*args, **kwargs), handler[-1]
        callback = getattr(cls, func)

        d = callback(*args, **kwargs) or None
        return d

    def get_data(self, event, action):
        event_affected = event['affected_objects']
        action_affected = action['affected_objects']

        data = db.find_many_records("Exec_data", {"workflow_id": event['workflow_id']})['data']
        data_retrieved = dict()
        global_data = data['global']
        global_objects = event_affected['global']+action_affected['global']
        for obj in global_objects:
            data_retrieved[obj] = global_data[obj]

        local_data = data['local']
        local_objects = event_affected['local']+action_affected['local']

        for obj in local_objects:
            for local in local_data[obj[0]]:
                if local['name'] == obj[1]:
                    data_retrieved[(obj[0], obj[1])] = local['value']

        return data_retrieved

    def merge(self, d1, d2):
        d = dict()
        d['global'] = {**d1['global'], **d2['global']}
        old_local_data = d1['local']
        new_local_data = d2['local']

        new_data = list()
        for key, val in new_local_data.items():
            if key in old_local_data.items():
                new_data.append({key: val})

        for key, val in old_local_data.items():
            if key not in new_local_data.items():
                new_data.append({key: val})

        d['local'] = new_data
        return d

    def update(self, d1, d2, id):
        d = self.merge(d1, d2)

        global_vars = set(db.find_one_record("Globals", {'workflow_id': id})['globals'])
        global_set = set(d.keys()).intersection(global_vars)
        local_set = set(d.keys()).difference(global_set)

        old_data = db.find_one_record("Exec_data", {"workflow_id": id})['data']
        data = old_data
        for i in global_set:
            data['global'][i] = d[i]

        data['global'] = {**d['global'], **old_data['global']}

        local_data = db.find_one_record("Exec_data", {"workflow_id": id})['data']['local']
        for key in local_set:
            local_data[key] = d[key]

        data['local'] = local_data
        db.update_record("Exec_data", old_data, data)

    def process_rule(self, rule, event, *args, **kwargs):
        rule_data = db.find_one_record("Rules", {'_id': rule})
        condition = Condition(db.find_one_record("Conditions", {'_id': rule_data['condition']}))
        action = db.find_one_record("Actions", {'_id': rule_data['action']})
        data = self.get_data(event, action)
        # affected_objects = event['affected_objects']

        if condition.check(data):
            if action['handler']:
                output = self.run_handler(action, data, *args, **kwargs)
                self.update(data, output, rule_data['workflow_id'])
            return action['raised_events']
        return None

    def dispatch_event(self, event, *args, **kwargs):
        """
        Dispatch an instance of Event class
        """
        # Dispatch the event to all the associated listeners
        event_data = db.find_one_record("Events", {'_id', event})
        raised_events = []
        if event['name'] in self._events.keys():
            rules = self._events[event['name']]

            for rule in rules:
                r_events = self.process_rule(rule, event_data, *args, **kwargs)
                if r_events:
                    raised_events.append(r_events)
        return raised_events

    def add_event_listener(self, event_type, listener):
        """
        Add an event listener for an event type
        """
        # Add listener to the event type
        if not self.has_listener(event_type, listener):
            listeners = self._events.get(event_type, [])

            listeners.append(listener)

            self._events[event_type] = listeners

    def remove_event_listener(self, event_type, listener):
        """
        Remove event listener.
        """
        # Remove the listener from the event type
        if self.has_listener(event_type, listener):
            listeners = self._events[event_type]

            if len(listeners) == 1:
                # Only this listener remains so remove the key
                del self._events[event_type]

            else:
                # Update listeners chain
                listeners.remove(listener)

                self._events[event_type] = listeners
