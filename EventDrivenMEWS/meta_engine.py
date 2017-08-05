from eventhandler import EventHandler


class MetaEngine:
    # Output of a task is stored in the data dict of a task with key='output'
    def __init__(self, mw, uw):
        self.mw = mw
        self.uw = uw

        self.mEHandler = EventHandler()
        self.uEHandler = EventHandler()

        self.mstart = self.get_start_event(mw)
        self.ustart = self.get_start_event(uw)

        self.mEHandler.add_event(self.mstart)

    def get_start_event(self,w):
        for event in w.events:
            if event.task.name.lower() == "start":
                return event
        return None

    def execute(self):
        acts = self.mEHandler.actions
        me = self.mstart
        while len(acts):
            for eve in me:
                self.mEHandler.register_action(eve, eve.task.action, eve.task.handler)
                self.mEHandler.fire(eve,ueh=self.uEHandler, uw = self.uw )
            acts = self.mEHandler.actions
            me = self.mEHandler.actions.keys()
