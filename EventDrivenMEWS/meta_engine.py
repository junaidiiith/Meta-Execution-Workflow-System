from eventhandler import EventHandler
from actionhandler import ActionHandler


class MetaEngine:

    def __init__(self, mw, uw):
        self.mw = mw
        self.uw = uw

        self.mEHandler = EventHandler()
        self.uEHandler = EventHandler()
        self.mAHandler = ActionHandler()
        self.uAHandler = ActionHandler()

        self.mstart = self.get_start_event(mw)
        self.ustart = self.get_start_event(uw)

        self.mEHandler.add_event(self.mstart)
        self.uEHandler.add_event(self.ustart)


    def get_start_event(self,w):
        event = None
        for event in w.events:
            if event.task.name.lower() == "start":
                return event
        return event

    def execute(self):
        acts = self.mEHandler.actions
        ue = self.ustart
        me = self.mstart
        while len(acts):
            for eve in me:
                self.mEHandler.register_action(eve, eve.task.action, eve.task.handler)
                self.mEHandler.fire()
            acts = self.mEHandler.actions
            me = self.mEHandler.actions.keys()


