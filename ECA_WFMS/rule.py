from mongo_database import Database


class Rule(object):
    def __init__(self, id):
        data = DB.find('Rules', {'_id', id})
        self._event = Event(data['event'])
        self._condition = Condition(data['condition'])
        self._action = Action(data['action'])

    @property
    def event(self):
        """
        Returns the event type
        """
        return self._event

    @property
    def condition(self):
        """
        Returns the data associated to the event
        """
        return self._condition

    @property
    def action(self):
        self._action
