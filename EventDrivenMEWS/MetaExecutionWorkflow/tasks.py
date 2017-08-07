class Tasks:
    def __init__(self, *args, **kwargs):
        self.type = 'meta'
        self.uEHandler = kwargs['ueh']
        self.uw = kwargs['uw']

    def create_workflow_instance(self,*args,**kwargs):
        self.uEHandler = kwargs['ueh']
        self.uw = kwargs['uw']
        data = dict()
        data['User Workflow Handler'] = kwargs['ueh']
        data['User Workflow'] = kwargs['ue']
        return data

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
        ue = self.uEHandler.actions.keys()
        if ue is None:
            ue = self.get_start_event()

        while len(ue):
            for eve in ue:
                self.uEHandler.register_action(eve, eve.task.action, eve.task.handler)
                self.uEHandler.fire(eve)
            ue = self.uEHandler.actions.keys()