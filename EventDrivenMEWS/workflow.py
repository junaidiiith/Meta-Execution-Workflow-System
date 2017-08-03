from task import Task
import uuid
import json
import task
from condition import *
from eca_rule import ECA


class Workflow:
    __slots__ = ['id', 'title', 'events', 'actions', 'conditions', 'tasks','graph', 'eca_rules','roles','resources']

    def __init__(self,*args,**kwargs):
        self.id = uuid.uuid4()
        # self.title = kwargs['title']
        self.actions = set()
        self.events = set()
        self.conditions = set()
        self.tasks = set()
        self.roles = set()
        self.resources = set()
        self.graph = {}


    def add_to_db(self):
        pass

    def define_roles(self):
        print("Enter roles. Press [ENTER] to quit adding role")
        while True:
            role = input("Enter a role")
            if not role:
                break
            self.roles.add(role)

    def define_resources(self):
        print("Enter the location of resources. Press [ENTER] to quit adding resources")
        while True:
            resource = input("Enter the location of resource")
            if not resource:
                break
            self.resources.add(resource)

    def create_tasks(self):
        tasks = set()
        print("Defining tasks for the workflow")
        while True:
            t = Task()
            tasks.add(t)
            i = input("1: Add task [Enter]: Completed defining tasks")
            if i != 1:
                break
        self.tasks = tasks
        self.add_to_db()

    def create_sequence(self):
        tasks = self.tasks
        graph = {}
        temp = {}
        print("These are the tasks. Select the output tasks of each task")
        for i,task in enumerate(tasks,1):
            print(i,")Task name is: ", task.name)
            temp[i] = task.id

        for t in self.tasks:
            while True:
                i = input("Enter the index of output task of "+t.name)
                typ = input("Choose the type of condition\n 1) Arithmetic 2)Database 3) External 4) System")
                exp = input("Enter the expression of condition for this task to be executed in the format"
                            "Operand(space)Operator(space)Constant (For Arithmetic)")
                c = {'type':typ, 'expression': exp }
                t.output_tasks.add(temp[i],c)
                print("Task and condition added")
                i = input("press [Enter] to move on to the next task or 1 to add more output tasks")
                if not len(i):
                    break
            graph[t] = t.output_tasks
        self.graph = graph
        self.create_events_condition_action_rules()

    def load(self, json_file):
        f = open(json_file)
        data = json.load(f)

        #tasks
        for t in data['tasks']:
            self.tasks.add(task.create_task(t.name, t))
        self.add_to_db()
        #graph
        self.graph = data['graph']
        self.create_events_condition_action_rules()

    def create_events_condition_action_rules(self):

        for t in self.tasks:
            self.events.add(t.event)
            self.actions.add(t.action)
            for o in t.output_tasks:
                tsk,c = o
                s = None
                cond = None
                if c.type.lower() == 'arithmetic':
                    desc = tuple(c.expression.split())
                    a = ArithmeticEqualityCondition(desc)
                    s = a.get_condition()
                    cond = Condition(tsk.event.id,s)
                else:
                    cond = Condition(tsk.event.id)
                self.conditions.add(cond)
                self.eca_rules.append(ECA(tsk.event,cond,tsk.action))
