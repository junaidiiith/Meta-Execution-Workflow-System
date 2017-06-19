from uuid import uuid4
import json


class Task:

    def __init__(self,wf,name,state='FUTURE',**kwargs):
        self.id = uuid4()
        self.state = state
        self.wf = wf
        self.workflow = kwargs.get('workflow')
        self.name = name
        self.data = {}
        self.owner = None
        self.input_tasks = []
        self.output_tasks= []
        self.variables = {}
        self.agent = None
        self.cls = None
        self.manual = False
        self.description = ''
        self.type = None
        self.set_values()

    def set_values(self,name):
        f = open(self.wf)
        data = json.load(f)
        self.type = data['type']
        task = data['task_specs'][self.name]
        self.cls = task['class']
        self.data = task['data']
        self.owner = task['owner']
        self.variables = task['vars']
        self.input_tasks = task['input_tasks']
        self.output_tasks = task['output_tasks']
        self.agent = task['class']
        self.manual = task['manual']
        self.description = task['description']
        self.update_db(self)

    def update_db(self):
        pass

    def get_id(self):
        return self.id

    def get_state(self):
        return self.state

    def get_data(self):
        return self.data

    def get_owner(self):
        return self.owner

    def get_workflow(self):
        return self.workflow

    def get_variables(self):
        return self.variables

    def get_input_tasks(self):
        return self.input_tasks

    def get_output_tasks(self):
        return self.output_tasks

    def set_state(self,state):
        self.state = state

    def set_data(self,data):
        self.data = data

    def set_owner(self,owner):
        self.owner = owner

    def set_workflow(self,wf):
        self.workflow = wf

    def set_variables(self,variables):
        self.variables = variables

    def set_input_tasks(self,tasks):
        self.input_tasks = tasks

    def set_output_tasks(self,tasks):
        self.output_tasks = tasks

    def execute(self,**kwargs):
        parts = self.agent.rsplit('.', 1)
        m = __import__(parts[0])
        i = getattr(m,parts[1])()
        sw_tasks = None
        if self.type == 'meta':
            sw = kwargs.get('sw')
            sw_tasks = kwargs.get('sw_tasks')
            sw_tasks = i.run(self,sw=sw, sw_tasks=sw_tasks)
        else:
            i.run(self)

        parts = self.cls.rsplit('.', 1)
        m = __import__(parts[0])
        i = getattr(m, parts[1])()
        self.set_output_tasks(i.run(self))
        self.update_db()
        return self.get_output_tasks(), sw_tasks
