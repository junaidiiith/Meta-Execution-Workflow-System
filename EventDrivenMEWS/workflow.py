import uuid
import json
import task
from condition import *
from eca_rule import ECA


class Workflow:
    __slots__ = ['id', 'title', 'type','description', 'events', 'actions', 'conditions', 'tasks','graph', 'eca_rules','roles','resources']

    def __init__(self,title=None, type=None,description=None,*args,**kwargs):
        self.id = str(uuid.uuid4())

        if not title:
            title = input("Enter the title of the workflow")
        self.title = title

        if not type:
            type = input("Enter the type of the workflow")
        self.type = type

        if not description:
            description = input("Enter the description of the workflow")
        self.description = description

        self.actions = dict()
        self.events = dict()
        self.conditions = dict()
        self.tasks = dict()
        self.roles = set()
        self.resources = set()
        self.graph = dict()
        self.eca_rules = set()

    # def add_to_db(self):
    #     pass

    def define_roles(self,roles=None):
        if roles:
            for role in roles:
                self.roles.add(role)
        else:
            print("Enter roles. Press [ENTER] to quit adding role")
            while True:
                role = input("Enter a role")
                if not role:
                    break
                self.roles.add(role)

    def define_resources(self,resources=None):
        if resources:
            for resource in resources:
                self.resources.add(resource)
        else:
            print("Enter the location of resources. Press [ENTER] to quit adding resources")
            while True:
                resource = input("Enter the location of resource")
                if not resource:
                    break
                self.resources.add(resource)

    def load_tasks(self, tasks):
        f = open(tasks)
        tasks = json.load(f)['tasks']
        for values in tasks:
            t = task.create_task(**values)
            self.tasks[t.id] = t

    def create_tasks(self):
        tasks = dict()
        print("Defining tasks for the workflow")
        while True:
            t = task.create_task()
            tasks[t.id] = t
            i = input("1: Add task [Enter]: Completed defining tasks")
            if i != "1":
                break
        self.tasks = tasks
        # self.add_to_db()


    def create_graph(self,graph):
        g = open(graph)
        self.graph = json.load(g)

        for k,v in self.graph.items():
            tsk = self.tasks[k.lower()]
            out_tasks = []
            event_cond = []
            for value in v:
                out = self.tasks[value['action']]
                conds = value['conditions']
                d = dict()
                d['action'] = out.id
                d['conditions'] = conds
                out_tasks.append(d)
                d = dict()
                d['event'] = out.event.id, out.event.description
                d['conditions'] = conds
                event_cond.append(d)
            tsk.output_tasks = out_tasks
            tsk.action.event_conditions = event_cond


    def pretty_print(self, json_dict_or_string, f):
        def pp_json(json_dict_or_string, f, sort=True, indents=4):
            fl = open(f, 'w')
            if type(json_dict_or_string) is str:
                fl.write(json.dumps(json.loads(json_dict_or_string), sort_keys=sort, indent=indents))
            else:
                fl.write(json.dumps(json_dict_or_string, sort_keys=sort, indent=indents))
        pp_json(json_dict_or_string,f)

    def write_graph_to_file(self, f):
        graph = dict()
        for k,v in self.graph.items():
            graph[str(k)] = v
        self.graph = graph

        self.pretty_print(json.dumps(graph),f)


    def create_sequence(self, graph=None):
        if graph:
            self.create_graph(graph)
        else:
            for k,t in self.tasks.items():
                t.event.set_task(t)
                t.action.set_task(t)
                self.events[t.id] = t.event
                self.actions[t.id] = t.action

            tasks = self.tasks
            graph = {}
            temp = {}
            print("These are the tasks. Select the output tasks of each task")
            for i, tsk in enumerate(self.tasks.values(),1):
                print(i,")Task name is: ", tsk.name)
                temp[i] = tsk

            for k,t in self.tasks.items():
                i = input("Enter the index of output task of " + t.name)
                out_tasks = []
                event_conditions = []
                while len(i):
                    conditions = []
                    typ = input("Choose the type of condition\n 1) Arithmetic 2)Database 3) External 4) System")
                    while typ:
                        c = dict()
                        exp = input("Enter the expression of condition for this task to be executed in the format"
                                "Operand(space)Operator(space)Constant (For Arithmetic) ")
                        if exp:
                            c['type'] = typ
                            c['expression'] = exp
                        conditions.append(c)
                        typ = input("Choose the type of condition\n 1) Arithmetic 2)Database 3) External 4) System."
                                    "Press [Enter] to stop adding condition ")

                    tsk = temp[int(i)]
                    d = dict()
                    d['conditions'] = conditions
                    d['action'] = tsk.id
                    out_tasks.append(d)
                    d = dict()      #Linking output tasks and corr. conditions to task
                    d['event'] = (tsk.event.id, tsk.event.description)
                    d['conditions'] = conditions
                    event_conditions.append(d)  #Linking output actions and corr. conditions to task
                    # print(d)
                    print("Task and condition added")
                    i = input("press [Enter] to move on to the next task or index of the next output task")
                t.output_tasks = out_tasks
                t.action.event_conditions = event_conditions
                graph[t.name] = t.output_tasks

            self.graph = graph
        self.write_graph_to_file(self.title+"graph.json")
        self.create_events_condition_action_rules()

    def load(self, json_file):
        f = open(json_file)
        data = json.load(f)

        #tasks
        self.load_tasks(data['tasks'])
        # self.add_to_db()
        #graph
        self.create_graph(data['graph'])
        # self.create_events_condition_action_rules()

    def put(self):
        data = dict()
        data['title'] = self.title
        data['type'] = self.type
        data['description'] = self.description
        tasks = []
        for task in self.tasks:
            tasks.append(task.put())

        data['tasks'] = tasks
        data['graph'] = self.graph

        return data

    def to_json(self, data=None):
        if not data:
            data = self.put()

        with open(self.title+'.json', 'w') as fp:
            json.dump(data, fp)

    def create_events_condition_action_rules(self):
        for k,t in self.tasks.items():
            for o in t.output_tasks:
                conditions = o['conditions']
                tsk = self.tasks[o['action']]
                conds = []
                for condition in conditions:
                    tp = condition['type'].lower()
                    if tp == 'arithmetic':
                        expr = condition['expression'].split()

                        a = ArithmeticEqualityCondition(expr[0],expr[1],expr[2])
                        s = a.get_condition()

                        cond = Condition(tsk.event.id,s)
                    else:
                        cond = Condition(tsk.event.id)
                    if not cond:
                        self.conditions[cond.id] = cond
                    conds.append(cond)

                self.eca_rules.add(ECA(tsk.event,conds,tsk.action))
        f = dict()

        for eca in self.eca_rules:
            f[eca.id] = eca.put()

        self.pretty_print(json.dumps(f),self.title+"_eca.json")
