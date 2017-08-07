from uuid import uuid4


class ECA:
    __slots__ = ['id','event', 'condition', 'action']

    def __init__(self,event=None,condition=None,action=None):
        self.id = uuid4()
        self.event = (event.id, event._description)
        self.condition = (condition.id, condition._description)
        self.action = (action.id, action._description)

    def put(self):
        data = dict()
        data['event'] = self.event
        data['condition'] = self.condition
        data['action'] = self.action
        return data