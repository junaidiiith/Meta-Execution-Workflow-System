import json
import task
from database_funcs import Database
from uuid import uuid4


class Workflow:
    __slots__ = ['id', 'dbs', 'globals', 'constants', 'title',
                 'type', 'description', 'tasks', 'graph', 'roles', 'resources','content']

    def __init__(self, json_file=None, *args, **kwargs):
        self.id = str(uuid4())
        self.dbs = Database()

        if json_file:
            self.title = json_file['title']
            self.type = json_file['type']
            self.description = json_file['description']
        else:
            self.title = input("Enter the title of the workflow")
            self.type = input("Enter the type of the workflow")
            self.description = input("Enter the description of the workflow")

        self.roles = list()
        self.define_roles(json_file)

        self.resources = list()
        self.define_resources(json_file)

        self.tasks = list()
        self.define_tasks(json_file)

        self.constants = dict()
        self.define_constants(json_file)

        self.globals = dict()
        self.define_globals(json_file)

        if not json_file:
            self.define_graph()

        self.content = self.store()
        print("-----------------Workflow object creation successful-------------")

    def define_roles(self, json_file=None):
        if json_file:
            for role in json_file['roles']:
                self.roles.append(role)
        else:
            print("Enter roles. Press [ENTER] to quit adding role")
            while True:
                role = input("Enter a role")
                if not role:
                    break
                self.roles.append(role)

    def define_resources(self, json_file=None):
        if json_file:
            for resource in json_file['resources']:
                self.resources.append(resource)
        else:
            print("Enter the location of resources. Press [ENTER] to quit adding resources")
            while True:
                resource = input("Enter the location of resource")
                if not resource:
                    break
                self.resources.append(resource)

    def define_globals(self, json_file=None):
        print("Initializing the default values of the global variables")
        if json_file:
            for key, value in json_file['globals'].items():
                self.globals[key] = value
        else:
            self.globals['state'] = "Not started"
            while True:
                var_name = input("Enter the name of a global variable")
                if len(var_name):
                    val = input("Enter the default value")
                    assert val is not None
                    self.globals[var_name] = val
                else:
                    break

    def define_constants(self, json_file=None):
        print("Initializing the default values of the constant variables")
        if json_file:
            for key, value in json_file['constants'].items():
                self.constants[key] = value
        else:
            while True:
                var_name = input("Enter the name of a constant variable")
                if len(var_name):
                    val = input("Enter the default value")
                    assert val is not None
                    self.constants[var_name] = val
                else:
                    break

    def define_tasks(self, json_file=None):
        tasks = dict()
        if json_file:
            for tsk in json_file['tasks']:
                t = task.create_task(self.id, **tsk)
                tasks[t.id] = t
                self.dbs.add_to_database("Tasks", t.put())
                self.tasks.append(self.dbs.find_one_record("Tasks",t.put()))

            for tsk in json_file['tasks']:
                outevents = []
                # print("Output tasks of ",tsk['name'],"are ",len(tsk['output_tasks']))
                for out_task in tsk['output_tasks']:
                    # print(outtask['task'])
                    conditions = out_task['conditions']
                    outtskdata = self.dbs.find_one_record("Tasks", {"workflow_id": self.id, "name": out_task['task']})
                    outevent = outtskdata['event']
                    outevents.append(outevent)
                    oevent = self.dbs.find_one_record("Events", {"_id": outevent})
                    oevent['conditions'] = []
                    for condition in conditions:
                        condition['workflow_id'] = self.id
                        condition['event_id'] = outevent
                        self.dbs.add_to_database("conditions", condition)
                        condition_id = self.dbs.find_one_record("conditions", condition)['_id']
                        oevent['conditions'].append(condition_id)
                    self.dbs.update_record("Events", {'_id': outtskdata['event']}, oevent)
                dbtask = self.dbs.find_one_record("Tasks", {"workflow_id": self.id, "name": tsk['name']})
                action = self.dbs.find_one_record("Actions", {'_id': dbtask['action']})
                action['output_events'] = outevents
                self.dbs.update_record("Actions", {'_id': action['_id']}, action)
        else:
            print("Defining tasks for the workflow")
            while True:
                t = task.create_task(self.id)
                tasks[t.id] = t
                self.dbs.add_to_database("Tasks", t.put())
                self.tasks.append(self.dbs.find_one_record("Tasks", t.put()))
                i = input("1: Add task [Enter]: Completed defining tasks")
                if i != "1":
                    break

    def get_expression(self):
        type = input("Choose 1) Global 2) Task output variable")
        if type == "1":
            operand = {"type":'global', 'variable': input("Enter the variable name for comparison")}
        else:
            name = input("Enter the task name")
            variable = input("Enter the variable name for comparison")
            operand = {'type':'local', 'task':{'name':name, 'variable':variable}}

        operator = input("Enter the operator")
        constant = input("Enter the constant to compare")
        return {'operand':operand,'operator':operator, 'constant':constant}

    def define_graph(self):
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
                c['expression'] = {'operand':{'type':'local','task':{'name':task['name'], 'variable': 'state'}}, 'operator':'==', 'constant':'finished'}
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
                evnt['conditions'] += conditions

                self.dbs.update_record("Events",{'_id':tsk['event']}, evnt)
                out_events.append(evnt['_id'])
                print("Task and condition added")
                i = input("press [Enter] to move on to the next task or index of the next output task")

            act = self.dbs.find_one_record("Actions",{'_id':task['action']})

            act['output_events'] = out_events
            self.dbs.update_record("Actions", {'_id':task['action']}, act)

        record = {"workflow_id":self.id}
        events = self.dbs.find_many_records("Events",record)
        for event in events:
            print(event['task'])
            typ = input("Enter the type of conditions join/and/or for this task [default 'AND']")
            event['condition_type'] = typ
            self.dbs.update_record("Events", {'_id':event['_id']}, event)

    def store(self):
        data = dict()
        data['title'] = self.title
        data['type'] = self.type
        data['description'] = self.description
        data['roles'] = self.roles
        data['resources'] = self.resources
        data['globals'] = self.globals
        data['constants'] = self.constants
        for task in self.tasks:
            outtasks = []
            action = self.dbs.find_one_record("Actions",{'_id': task['action']})
            out_events = action['output_events']
            for event in out_events:
                event_data = self.dbs.find_one_record("Events",{'_id':event})
                outtask = event_data['task']
                conditions = event_data['conditions']
                outcond = []
                for condition in conditions:
                    d = dict()
                    cond_data = self.dbs.find_one_record("conditions",{'_id':condition})
                    d['expression'] = cond_data['expression']
                    d['type'] = cond_data['type']
                    outcond.append(d)
                outtasks.append({'task':outtask, 'conditions':outcond})
            task['output_tasks'] = outtasks
        tsks = []
        for tsk in self.tasks:
            d = dict()
            d['name'] = tsk['name']
            d['owner'] = tsk['owner']
            d['handler'] = tsk['handler']
            d['type'] = tsk['type']
            d['output_tasks'] = tsk['output_tasks']
            d['description'] = tsk['description']
            d['manual'] = tsk['manual']
            d['affected_objects'] = tsk['affected_objects']
            tsks.append(d)
        data['tasks'] = tsks
        temp = data
        temp['id'] = self.id
        self.dbs.add_to_database("Workflow", temp)
        return data

    def to_json(self):
        content = self.content
        data = dict()
        for key, value in content.items():
            if key == "_id" or key == 'id':
                continue
            data[key] = value
        self.pretty_print(data, self.title+'.json')

    def pretty_print(self, json_dict_or_string, f):
        def pp_json(json_dict_or_string, f, sort=True, indents=4):
            fl = open(f, 'w')
            if type(json_dict_or_string) is str:
                fl.write(json.dumps(json.loads(json_dict_or_string), sort_keys=sort, indent=indents))
            else:
                fl.write(json.dumps(json_dict_or_string, sort_keys=sort, indent=indents))
        pp_json(json_dict_or_string,f)