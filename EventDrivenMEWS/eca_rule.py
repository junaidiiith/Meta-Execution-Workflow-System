from uuid import uuid4


class ECA:
    __slots__ = ['id','event', 'condition', 'action']

    def __init__(self,event=None,condition=None,action=None):
        self.id = uuid4()
        self.event = event
        self.condition = condition
        self.action = action
