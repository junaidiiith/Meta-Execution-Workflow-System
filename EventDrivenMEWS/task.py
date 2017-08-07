from uuid import uuid4
from states import TaskStates
from event import Event
from action import Action

class Task:
    __slots__ = ['id', 'name', 'description', 'handler', 'state', 'owner', 'type', 'manual', 'data', 'output_tasks','event','action']

    def __init__(self,name=None,type=None,*args,**kwargs):
        self.id = uuid4()
        self.state = TaskStates.NOT_STARTED
        self.name = name
        self.data = {}
        self.owner = None
        self.output_tasks = set()
        self.handler = None
        self.manual = False
        self.description = ''
        self.type = type
        self.event = Event()
        self.action = Action()
        self.set_values(**kwargs)

    def set_values(self,**task):
        self.handler = task['handler']
        self.data = task['data']
        self.owner = task['owner']
        self.output_tasks = task['output_tasks']
        self.manual = task['manual']
        self.description = task['description']

    def get_id(self):
        return self.id

    def get_state(self):
        return self.state

    def get_data(self):
        return self.data

    def get_owner(self):
        return self.owner

    def get_output_tasks(self):
        return self.output_tasks

    def set_state(self,state):
        self.state = state

    def set_data(self,data):
        self.data = data

    def set_owner(self,owner):
        self.owner = owner

    def set_output_tasks(self,tasks):
        self.output_tasks = tasks

    def put(self):
        data = {}
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                data[attr] = self.attr
        return data

    def execute(self,**kwargs):
        pass

def create_task(name=None, **values):

    if not name:
        name = input("Enter the name of the task")
    t = Task(name)
    if not values:
        print("Enter the attributes of the task as a tuple")
        values['id'] = uuid4()
        values['description'] = input("Enter the description of the task")
        values['type'] = input("Enter the type of  task --> meta/user")
        values['owner'] = input("Enter the owner of the task")
        values['handler'] = input("Enter the name of class and function to execute task with a space")
        data = {}
        while True:
            var = input("Enter the name of the task variable/constant")
            if var is None:
                break
            val = input("Enter the value of the task variable")
            data[var] = val

        values['data'] = data
    t.set_values(values)
    return t
