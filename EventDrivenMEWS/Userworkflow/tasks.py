class Tasks:
    def __init__(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        print("Starting start task")

    def add_application(self, *args, **kwargs):
        print("Adding application")

    def check_cgpa(self, *args, **kwargs):
        print("Checking cgpa")

    def accept_application(self, *args, **kwargs):
        print("Email sent succesfully")

    def reject_application(self, *args, **kwargs):
        print("Rejected candidate")

    def end(self, *args, **kwargs):
        print("User workflow execution ended")