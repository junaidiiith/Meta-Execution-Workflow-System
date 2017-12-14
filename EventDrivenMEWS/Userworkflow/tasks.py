class Tasks:
    def __init__(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        print("Starting start task")
        kwargs['state'] = "started"
        return kwargs

    def add_application(self, *args, **kwargs):
        print("Adding application")
        data = dict()
        data['cgpa'] = 8
        data['name'] = "Junaid"
        data['email'] = "emailid"
        data['phone'] = "123"
        kwargs = {**kwargs, **data}
        return kwargs

    def check_cgpa(self, *args, **kwargs):
        kwargs['output'] = True
        print("Checking cgpa")
        return kwargs

    def call_interview(self, *args, **kwargs):
        kwargs['output'] = True
        print("Email sent succesfully")
        return kwargs

    def reject_application(self, *args, **kwargs):
        kwargs['output'] = True
        print("Rejected candidate")
        return kwargs

    def end(self, *args, **kwargs):
        print("User workflow execution ended. The required output is this!""")