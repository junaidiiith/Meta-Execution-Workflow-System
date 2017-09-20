import json
import task
from database_funcs import Database
from uuid import uuid4


class Workflow:
    __slots__ = ['id','dbs','globals', 'constants','title', 'type','description', 'tasks','graph', 'roles','resources']

    def __init__(self,title=None, typ=None,description=None,*args,**kwargs):
        self.id = str(uuid4())
        self.dbs = Database()
        self.dbs.add_to_database("Workflow",{'id':self.id})

        if not title:
            title = input("Enter the title of the workflow")
        self.title = title

        if not typ:
            typ = input("Enter the type of the workflow")
        self.type = typ

        if not description:
            description = input("Enter the description of the workflow")
        self.description = description

        self.tasks = list()
        self.roles = list()
        self.resources = list()
        self.constants = dict()
        self.define_roles()
        self.define_resources()
        self.define_constants()
        self.graph = dict()

        self.globals = dict()
    #     pass

    def add_global_data(self):
        for k,v in self.globals.items():
            record = {"type": "global", 'variable': k, 'value': v, "workflow_id": self.id}
            self.dbs.add_to_database("Data", record)

    def define_roles(self,roles=None):
        if roles:
            for role in roles:
                self.roles.append(role)
        else:
            print("Enter roles. Press [ENTER] to quit adding role")
            while True:
                role = input("Enter a role")
                if not role:
                    break
                self.roles.append(role)
        self.dbs.add_to_database("Roles",{'roles':roles})

    def define_resources(self,resources=None):
        if resources:
            for resource in resources:
                self.resources.append(resource)
        else:
            print("Enter the location of resources. Press [ENTER] to quit adding resources")
            while True:
                resource = input("Enter the location of resource")
                if not resource:
                    break
                self.resources.append(resource)

        self.dbs.add_to_database("Resources",{'resources':resources})

    def define_globals(self):
        print("Initializing the default values of the global variables")
        while True:
            var_name = input("Enter the name of a global variable")
            if len(var_name):
                val = input("Enter the default value")
                assert val != None
                self.globals[var_name] = val
            else:
                break

    def define_constants(self):
        while True:
            var_name = input("Enter the name of a constant variable")
            if len(var_name):
                val = input("Enter the default value")
                assert val != None
                self.constants[var_name] = val
            else:
                break

    def load_tasks(self, tasks):
        f = open(tasks)
        tasks = json.load(f)['tasks']
        for values in tasks:
            t = task.create_task(self.id, **values)
            self.tasks[t.id] = t
            self.dbs.add_to_database("Tasks", t.put())

    def create_tasks(self):
        tasks = dict()
        print("Defining tasks for the workflow")
        while True:
            t = task.create_task(self.id)
            tasks[t.id] = t
            self.dbs.add_to_database("Tasks", t.put())
            i = input("1: Add task [Enter]: Completed defining tasks")
            if i != "1":
                break
        tasks = self.dbs.find_many_records("Tasks",{"workflow_id":self.id})
        for tsk in tasks:
            self.tasks.append(tsk)
        self.define_globals()
        # self.add_to_db()

    def create_graph(self,graph):
        pass
    #     g = open(graph)
    #     self.graph = json.load(g)
    #
    #     for k,v in self.graph.items():
    #         tsk = self.tasks[k.lower()]
    #         out_events = []
    #         event_cond = []
    #         for value in v:
    #             out = self.tasks[value['action']]
    #             conds = value['conditions']
    #             d = dict()
    #             d['action'] = out.id
    #             d['conditions'] = conds
    #             out_events.append(d)
    #             d = dict()
    #             d['event'] = out.event.id, out.event.description
    #             d['conditions'] = conds
    #             event_cond.append(d)
    #         tsk.output_tasks = out_events
    #         tsk.action.event_conditions = event_cond


    def pretty_print(self, json_dict_or_string, f):
        def pp_json(json_dict_or_string, f, sort=True, indents=4):
            fl = open(f, 'w')
            if type(json_dict_or_string) is str:
                fl.write(json.dumps(json.loads(json_dict_or_string), sort_keys=sort, indent=indents))
            else:
                fl.write(json.dumps(json_dict_or_string, sort_keys=sort, indent=indents))
        pp_json(json_dict_or_string,f)

    # def write_graph_to_file(self, f):
    #     graph = self.dbs.find_one_record({'workflow_id':self.id})
    #     self.pretty_print(json.dumps(graph),f)

    def get_expression(self):
        type = input("Choose 1) Global 2) Task output variable")
        if type == "1":
            operand = {"type":'global', 'variable': input("Enter the variable name for comparison")}
        else:
            name = input("Enter the task name")
            variable = input("Enter the variable name for comparison")
            operand = {'type':'local', 'expression':{'name':name, 'variable':variable}}

        operator = input("Enter the operator")
        constant = input("Enter the constant to compare")
        return {'operand':operand,'operator':operator, 'constant':constant}

    def create_sequence(self, graph=None):
        if graph:
            self.create_graph(graph)
        else:

            graph = {}
            temp = []
            i = 0
            print("These are the tasks. Select the output tasks of each task")
            for tsk in self.tasks:
                print(i+1,")Task name is: ", tsk['name'])
                temp.append(tsk)
                i += 1

            for task in self.tasks:
                i = input("Enter the index of output task of " + task['name'])
                out_events = []
                while len(i):
                    tsk = temp[int(i)-1]
                    conditions = []
                    c = dict()
                    c['type'] = 'Arithmetic'
                    c['expression'] = {'operand':{'type':'local','expression':{'name':task['name'], 'variable': 'state'}}, 'operator':'==', 'constant':'finished'}
                    c['event_id'] = tsk['event']
                    c['workflow_id'] = self.id
                    self.dbs.add_to_database("conditions",c)
                    c_id = self.dbs.find_one_record("conditions",c)['_id']
                    conditions.append(c_id)
                    typ = input("Choose the type of condition\n 1) Arithmetic 2)Database 3) External 4) System")
                    while typ:
                        c = dict()
                        exp = self.get_expression()
                        if exp:
                            c['type'] = typ
                            c['expression'] = exp
                            c['event_id'] = tsk['event']
                            c['workflow_id'] = self.id
                            self.dbs.add_to_database("conditions",c)
                            c_id = self.dbs.find_one_record("conditions", c)['_id']
                        conditions.append(c_id)
                        typ = input("Choose the type of condition\n 1) Arithmetic 2)Database 3) External 4) System."
                                    "Press [Enter] to stop adding condition ")

                    evnt = self.dbs.find_one_record("Events",{'_id':tsk['event']})
                    evnt['conditions'].append(conditions)

                    self.dbs.update_record("Events",{'_id':tsk['event']}, evnt)
                    out_events.append(evnt['_id'])
                    print("Task and condition added")
                    i = input("press [Enter] to move on to the next task or index of the next output task")

                task['output_events'] = out_events
                act = self.dbs.find_one_record("Actions",{'_id':task['action']})

                act['output_events'] = out_events
                self.dbs.update_record("Actions", {'_id':task['action']}, act)
                graph[task['name']] = out_events

            self.graph = {"graph":graph,"workflow id":self.id}
        self.dbs.add_to_database("graph",self.graph)

        gid = self.dbs.find_one_record("graph", self.graph)['_id']

        n_record = {"tasks": [t['_id'] for t in self.tasks], "globals": self.globals, "resources":self.resources, "constants": self.constants,
                   "roles":self.roles, "graph": gid}

        o_record = self.dbs.find_one_record("Workflow",{'id':self.id})
        print(type(o_record), type(n_record))
        print(o_record), print(n_record)
        self.dbs.update_record("Workflow", o_record, n_record)
        self.add_global_data()


        record = {"workflow_id":self.id}
        events = self.dbs.find_many_records("Events",record)
        for event in events:
            print(event['task'])
            typ = input("Enter the type of conditions join/and/or for this task [default 'AND']")
            event['condition_type'] = typ
            self.dbs.update_record("Events", {'_id':event['_id']}, event)



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
        data['globals'] = self.globals
        return data

    def to_json(self, data=None):
        if not data:
            data = self.put()

        with open(self.title+'.json', 'w') as fp:
            json.dump(data, fp)

    # def create_events_condition_action_rules(self):
    #     for k,t in self.tasks.items():
    #         for o in t.output_tasks:
    #             conditions = o['conditions']
    #             tsk = self.tasks[o['action']]
    #             conds = []
    #             for condition in conditions:
    #                 tp = condition['type'].lower()
    #                 if tp == 'arithmetic':
    #                     expr = condition['expression']
    #
    #                     cond = Condition(tsk.event.id,expr)
    #                 else:
    #                     cond = Condition(tsk.event.id)
    #                 if not cond:
    #                     self.conditions[cond.id] = cond
    #                 conds.append(cond)
    #
    #             self.eca_rules.add(ECA(tsk.event,conds,tsk.action))
    #     f = dict()

        # for eca in self.eca_rules:
        #     f[eca.id] = eca.put()
        #
        # self.pretty_print(json.dumps(f),self.title+"_eca.json")
