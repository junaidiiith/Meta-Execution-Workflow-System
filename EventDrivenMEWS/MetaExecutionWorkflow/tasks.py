from database_funcs import Database
import sys


class Tasks:
    def __init__(self, *args, **kwargs):
        self.type = 'meta'
        # self.uEHandler = kwargs['ueh']
        # self.uw = kwargs['uw']

    def start(self,*args,**kwargs):
        print("Starting workflow tasks")


    def create_workflow_instance(self,*args,**kwargs):
        print("Creating workflow instance")
        # self.uEHandler = kwargs['ueh']
        # self.uw = kwargs['uw']
        # data = dict()
        # data['User Workflow Handler'] = kwargs['ueh']
        # data['User Workflow'] = kwargs['ue']
        # return data

    def get_a_task(self,*args,**kwargs):
        print("Getting a task")
        # tasks = []
        # for event in self.uEHandler.actions.keys():
        #     tasks.append(event.task)
        # return tasks

    def check_resources(self,*args,**kwargs):
        print("Check resources")
        # for event in self.uEHandler.actions.keys():
        #     if not event.task.handler:
        #         return False
        # return True
    def check_task(self, *args, **kwargs):
        print("Checking next task!")

    # def get_start_event(self, w):
    #     event = self.dbs.find_one_record("Events", {"workflow_id": w.id, "task": "start"})
    #     if event:
    #         return event
    #     print("Start event not found!")
    #     sys.exit(0)

    def end(self, *args, **kwargs):
        print("Ending task of the workflow")

    def execute(self,*args,**kwargs):

        print("Executing execute function")
        # waiting_queue = self.uEHandler.actions.keys()
        # while len(waiting_queue):
        #     print("Registering events!")
        #     for eve in waiting_queue:
        #         task = Database().find_one_record("Tasks", {"name": eve.task, "workflow_id": self.uw.id})
        #         self.uEHandler.register_action(eve, task['action'])
        #
        #     print("Raising events!")
        #     for eve in waiting_queue:
        #         self.uEHandler.fire(eve)
        #     waiting_queue = self.uEHandler.actions.keys()
