from uuid import uuid4


class ECA:
    __slots__ = ['id','event', 'conditions', 'action']

    def __init__(self,event=None,conditions=None,action=None):
        self.id = str(uuid4())
        self.event = (event.id, event.description)
        self.conditions = [condition.description for condition in conditions]
        self.action = (action.id, action.description)

    def put(self):
        data = dict()
        data['event'] = self.event
        data['conditions'] = self.conditions
        data['action'] = self.action
        return data