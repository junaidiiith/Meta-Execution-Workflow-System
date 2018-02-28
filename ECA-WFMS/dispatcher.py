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

    def process_rule(self, rule, event, *args, **kwargs):
        data = DB.get('Data', {'_id': event.task.id})
        data = {**data, **Db.get('Data', 'global_data')}
        action = rule.action
        condition = rule.condition
        if condition.check(data):
            output = self.run_handler(action, event.data, *args, **kwargs)
            DB.update('Data', **output)

    def dispatch_event(self, event, *args, **kwargs):
        """
        Dispatch an instance of Event class
        """
        # Dispatch the event to all the associated listeners
        raised_events = []
        if event.type in self._events.keys():
            rules = self._events[event.type]

            for rule in rules:
                self.process_rule(rule, event, *args, **kwargs)
                raised_events.append(rule.action.events)
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
