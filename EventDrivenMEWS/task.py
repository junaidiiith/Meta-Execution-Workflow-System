from uuid import uuid4
from states import TaskStates
from event import Event
from action import Action
import json


class Task:
    __slots__ = ['id', 'name', 'description', 'handler', 'state', 'owner', 'type', 'manual', 'data', 'output_tasks','event','action']

    def __init__(self,name=None,type=None,*args,**kwargs):

        self.state = TaskStates.NOT_STARTED
        self.name = name.lower()
        self.id = name
        self.data = {}
        self.owner = None
        self.output_tasks = list()
        self.handler = None
        self.manual = False
        self.description = ''
        self.type = type
        self.event = Event(self)
        self.action = Action(self)

    def set_values(self,**values):
        self.handler = values['handler']
        self.data = values['data']
        self.owner = values['owner']
        try:
            self.output_tasks = values['output_tasks']
        except:
            pass
        self.manual = values['manual']
        self.description = values['description']
        self.type = values['type']

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

    def pretty_print(self, json_dict_or_string, f):
        def pp_json(json_dict_or_string, f, sort=True, indents=4):
            fl = open(f, 'w')
            if type(json_dict_or_string) is str:
                fl.write(json.dumps(json.loads(json_dict_or_string), sort_keys=sort, indent=indents))
            else:
                fl.write(json.dumps(json_dict_or_string, sort_keys=sort, indent=indents))

        pp_json(json_dict_or_string, f)

    def put(self):
        data = {}
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                data[attr] = self.attr
        return data

    def execute(self,**kwargs):
        pass


def create_task(**values):

    try:
        name = values['name'].lower()
    except:
        name = input("Enter the name of the task").lower()

    t = Task(name)
    if not values:
        print("Enter the attributes of the task as a tuple")
        values = dict()
        values['id'] = t.name
        values['description'] = input("Enter the description of the task")
        values['type'] = input("Enter the type of  task --> meta/user")
        values['owner'] = input("Enter the owner of the task")
        values['handler'] = tuple(input("Enter the name of module,class and function to execute task with a space or comma").split())
        values['manual'] = input("Enter if the task is manual or not")

        data = {}
        while True:
            var = input("Enter the name of the task variable/constant")
            if len(var) == 0:
                break
            val = input("Enter the value of the task variable")
            data[var] = val

        values['data'] = data
    t.set_values(**values)
    return t
