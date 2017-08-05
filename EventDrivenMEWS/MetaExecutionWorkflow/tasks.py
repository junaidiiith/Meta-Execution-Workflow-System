class Tasks:
    def __init__(self, *args, **kwargs):
        self.type = 'meta'
        self.uEHandler = kwargs['ueh']
        self.uw = kwargs['uw']

    def get_a_task(self):
        tasks = []
        for event in self.uEHandler.actions.keys():
            tasks.append(event.task)
        return tasks

    def check_resources(self):
        for event in self.uEHandler.actions.keys():
            if not event.task.handler:
                return False
        return True

    def get_start_event(self):
        for event in self.uw.events:
            if event.task.name.lower() == "start":
                return event
        return None

    def execute(self):
        acts = self.uEHandler.actions
        if acts is None:
            ue = self.get_start_event()
        ue = self.uEHandler.actions.keys()
        while len(acts):
            for eve in ue:
                self.uEHandler.register_action(eve, eve.task.action, eve.task.handler)
                self.uEHandler.fire(eve)
            acts = self.uEHandler.actions
            ue = self.uEHandler.actions.keys()