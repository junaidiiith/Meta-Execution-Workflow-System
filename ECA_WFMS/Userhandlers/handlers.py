class UserExecution(object):
    def __init__(self):
        pass

    def start(self):
        print("Workflow started")

    def get_a_task(self, event_queue):
        event = event_queue[0]
        task_id = Db.find_one_record("Events", {'_id': event['_id']})['task_id']
        return Db.find_one_record("Tasks", {'_id': task_id})

    def check_task(self, task):
        return task['name'] == "End"

    def check_resources(self, task):
        print("Resources checked")

    def execute(self, dispatcher, event):
        return dispatcher.dispatch_event(event)