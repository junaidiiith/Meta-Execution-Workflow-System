from eventhandler import EventHandler


class MetaEngine:
    # Output of a task is stored in the data dict of a task with key='output'
    def __init__(self, mw, uw):
        self.mw = mw
        self.uw = uw

        self.mEHandler = EventHandler(self.get_start_event(self.mw))
        self.uEHandler = EventHandler(self.get_start_event(self.uw))

    def get_start_event(self,w):
        for event in w.events:
            if event.task.name.lower() == "start":
                return event
        return None

    def execute(self):
        me = self.mEHandler.actions.keys()
        while len(me):
            for eve in me:
                self.mEHandler.register_action(eve, eve.task.action, eve.task.handler)
                self.mEHandler.fire(eve,ueh=self.uEHandler, uw = self.uw )
            me = self.mEHandler.actions.keys()
