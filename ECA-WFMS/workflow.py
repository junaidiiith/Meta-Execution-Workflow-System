from EventDrivenMEWS.mongo_database import Database
from uuid import uuid4
import json


class Workflow:
    __slots__ = ['id', 'dbs', 'globals', 'constants', 'title', 'start',
                 'type', 'description', 'tasks', '_events', 'roles', 'resources', 'content', '_rules']

    def __init__(self, json_file=None):
        self.id = str(uuid4())
        self.dbs = Database()

        if json_file:
            self.title = json_file['title']
            self.type = json_file['type']
            self.description = json_file['description']
        else:
<<<<<<< HEAD
            self.title = input("Enter the title of the workflow\n")
            self.type = input("Enter the type of the workflow\n")
            self.description = input("Enter the description of the workflow\n")
=======
            self.title = input("Enter the title of the workflow")
            self.type = input("Enter the type of the workflow")
            self.description = input("Enter the description of the workflow")
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
        self._events = None
        self._rules = None
        self.define_roles(json_file)
        self.define_resources(json_file)
        self.define_constants(json_file)
        self.define_globals(json_file)
        self.define_tasks(json_file)
        self.define_events(json_file)
        self.start = None
        self.define_eca_rules(json_file)
        self.content = self.store()
<<<<<<< HEAD
        self.to_json()
=======
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
        print("-----------------Workflow object creation successful-------------")

    def get(self, table):
        return self.dbs.find_many_records(table, {'_id': self.id})

    def define_roles(self, json_file=None):
        print("Defining roles")
        roles = list()
        if json_file:
            roles = json_file['roles']
        else:
            print("Enter roles. Press [ENTER] to quit adding role")
            while True:
<<<<<<< HEAD
                role = input("Enter a role\n")
=======
                role = input("Enter a role")
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                if not role:
                    break
                roles.append(role)
        self.dbs.add_to_database('Roles', {'roles': roles, 'workflow_id': self.id})

    def define_resources(self, json_file=None):
        print("Defining resources")
        resources = list()
        if json_file:
            resources = json_file['roles']
        else:
            print("Enter resources. Press [ENTER] to quit adding resources")
            while True:
<<<<<<< HEAD
                role = input("Enter a resource\n")
=======
                role = input("Enter a resource")
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                if not role:
                    break
                resources.append(role)
        self.dbs.add_to_database('Resources', {'resources': resources, 'workflow_id': self.id})

    def define_globals(self, json_file=None):
        print("Initializing the default values of the global variables")
        globals = dict()
        if json_file:
            for key, value in json_file['globals'].items():
                globals[key] = value
        else:
            globals['state'] = "Not started"
            while True:
<<<<<<< HEAD
                var_name = input("Enter the name of a global variable\n")
                if len(var_name):
                    val = input("Enter the default value\n")
=======
                var_name = input("Enter the name of a global variable")
                if len(var_name):
                    val = input("Enter the default value")
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                    assert val is not None
                    globals[var_name] = val
                else:
                    break
        self.dbs.add_to_database('Globals', {'globals': globals, 'workflow_id': self.id})

    def define_constants(self, json_file=None):
        constants = dict()
        print("Initializing the default values of the constant variables")
        if json_file:
            for key, value in json_file['constants'].items():
                constants[key] = value
        else:
            while True:
<<<<<<< HEAD
                var_name = input("Enter the name of a constant variable\n")
                if len(var_name):
                    val = input("Enter the default value\n")
=======
                var_name = input("Enter the name of a constant variable")
                if len(var_name):
                    val = input("Enter the default value")
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                    assert val is not None
                    constants[var_name] = val
                else:
                    break
        self.dbs.add_to_database('Constants', {'constants': constants, 'workflow_id': self.id})

    def define_tasks(self, json_file=None):
        print("Defining tasks")
        if json_file:
            tasks = json_file['tasks']
<<<<<<< HEAD
            t_data = dict()
            for task in tasks:
                for key, value in task.items():
                    t_data[key] = value
                t_data['workflow_id'] = self.id
                self.dbs.add_to_database("Tasks", t_data)
=======
            tdata = dict()
            for task in tasks:
                for key, value in task.items():
                    tdata[key] = value

                event_list = list()
                for event in tdata['input_events']:
                    db_event = self.dbs.add_to_database("Events", {'event': event, 'workflow_id': self.id})
                    tdata['event'] = db_event
                    event_list.append(db_event)
                tdata['input_events'] = event_list
                event_list = list()

                for event in tdata['output_events']:
                    db_event = self.dbs.add_to_database("Events", {'event': event, 'workflow_id': self.id})
                    tdata['event'] = db_event
                    event_list.append(db_event)
                tdata['output_events'] = event_list
                tdata['workflow_id'] = self.id
                self.dbs.add_to_database("Tasks", tdata)
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
        else:
            print("Defining tasks for the workflow")

            while True:
<<<<<<< HEAD
                add = input("Press [Enter] to stop adding tasks else any key\n")
                if len(add):
                    task = dict()
                    task['workflow_id'] = self.id
                    task['name'] = input("Enter the name of the task\n")
                    task['description'] = input("Enter the description of the task\n")
=======
                add = input("Press [Enter] to stop adding tasks else any key")
                if len(add):
                    task = dict()
                    task['workflow_id'] = self.id
                    task['name'] = input("Enter the name of the task")
                    task['description'] = input("Enter the description of the task")
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                    attribs = ['input_events', 'output_events', 'input_params', 'output_params']
                    for attrib in attribs:
                        l = []
                        while True:
<<<<<<< HEAD
                            add = input("Press [Enter] to stop adding "+attrib+'\n')
                            if add:
                                name = input("Enter the name of "+attrib[:-1]+'\n').upper()
=======
                            add = input("Press [Enter] to stop adding "+attrib)
                            if add:
                                name = input("Enter the name of "+attrib[:-1]).upper()
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                                l.append(name)
                            else:
                                break
                        task[attrib] = l
                    self.dbs.add_to_database("Tasks", task)
                else:
                    break
<<<<<<< HEAD
            task = dict()
            task['workflow_id'] = self.id
            task['name'] = 'start'
            task['description'] = 'starting task of a workflow'
            task['output_events'] = ["WORKFLOW_STARTED"]
            task['input_events'] = ["START_WORKFLOW"]
            task['input_params'] = []
            task['output_params'] = ['state']
            self.dbs.add_to_database("Tasks", task)

            task = dict()
            task['workflow_id'] = self.id
            task['name'] = 'end'
            task['description'] = 'ending task of a workflow'
            task['output_events'] = ["WORKFLOW_ENDED"]
            task['input_events'] = ["END_WORKFLOW"]
            task['input_params'] = []
            task['output_params'] = ['state']
            self.dbs.add_to_database("Tasks", task)
=======
                task = dict()
                task['workflow_id'] = self.id
                task['name'] = 'start'
                task['description'] = 'starting task of a workflow'
                task['output_events'] = ["WORKFLOW_STARTED"]
                task['input_events'] = ["START_WORKFLOW"]
                task['input_params'] = []
                task['output_params'] = 'state'
                self.dbs.add_to_database("Tasks", task)

                task = dict()
                task['workflow_id'] = self.id
                task['name'] = 'end'
                task['description'] = 'ending task of a workflow'
                task['output_events'] = ["WORKFLOW_ENDED"]
                task['input_events'] = ["END_WORKFLOW"]
                task['input_params'] = []
                task['output_params'] = ['state']
                self.dbs.add_to_database("Tasks", task)
>>>>>>> fb78d41550d471ef727838696ff62068320965e6

    def define_events(self, json_file=None):
        event_set = set()
        events = list()
        if json_file:
            events = json_file["Events"]
            for event in events:
                task = self.dbs.find_one_record("Tasks", {"name": event['task']})
                affected_objects = task['input_params']+task['output_params']
                if event not in event_set:
                    event_set.add(event)
                    events.append({'task_id': task['_id'], 'task_name': task['name'],
                                   "name": event['name'], 'description': event['description'],
                                   'affected_objects': affected_objects})
                    if event['name'] == 'START_WORKFLOW':
                        self.start = events[-1]
        else:
<<<<<<< HEAD
            tasks = self.dbs.find_many_records("Tasks", {'workflow_id': self.id})
=======
            tasks = self.dbs.find_many_records("Tasks", {})
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
            for task in tasks:
                if task['name'].lower() == "end":
                    for event in task['output_events']:
                        event_set.add((event, None))

                for event in task['input_events']:
                    if event not in event_set:
                        event_set.add(event)
<<<<<<< HEAD
                        description = input("Enter the description of the event: "+str(event)+'\n')
=======
                        description = input("Enter the description of the event"+str(event))
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                        affected_objects = self.choose_affected_objects(task['input_params']+task['output_params'])
                        events.append({'task_id': task['_id'], 'task_name': task['name'],
                                       "affected_objects": affected_objects,
                                       "name": event, 'description': description})
<<<<<<< HEAD
        for event in events:
            event['workflow_id'] = self.id
            self.dbs.add_to_database("Events", event)

        self._events = events
=======
        self._events = events
        for event in events:
            self.dbs.add_to_database("Events", {"workflow_id": self.id, "event": event})
>>>>>>> fb78d41550d471ef727838696ff62068320965e6

    def define_eca_rules(self, json_file=None):
        if json_file:
            rules = json_file['Rules']
            assert self._events is not None
            rule_ids = list()
            event_id = self.dbs.find_one_record("Events", {'name': rules[0]['event'], 'workflow_id': self.id})['_id']
            for rule in rules:
                condition = rule['condition']
                condition['workflow_id'] = self.id
                condition_id = self.dbs.add_to_database("Conditions", condition)
                action = rule['action']
                raised_events = action['raised_events']
                re_ids = list()
                for re in raised_events:
                    re_ids.append(str(self.dbs.find_one_record("Events",
                                                               {"workflow_id": self.id, "name": re})['_id']))

                action_id = self.dbs.add_to_database("Actions", {"workflow_id": self.id, "name": action['name'],
                                                                 'handler': action['handler'],
                                                                 'affected_objects': action['affected_objects'],
                                                                 'raised_events': re_ids})

                rule_ids.append(self.dbs.add_to_database("Rules", {"workflow_id": self.id,"name": rule['name'],
                                                                   "event": event_id,
                                                                   "condition": condition_id, "action": action_id}))

            self.dbs.update_record("Events", {"_id": event_id}, {"rules": rule_ids})
        else:
            print("Defining ECA rules")
            for event in self._events:
<<<<<<< HEAD
                print("Define rules for the event ", event['name'])
=======
                print("Define rules for the event", event['name'])
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                event_id = self.dbs.find_one_record("Events", {"workflow_id": self.id, 'name': event['name']})

                rule_ids = list()
                count = 0
                while True:
<<<<<<< HEAD
                    add = input("Press [Enter] to stop adding rules for an event "+event['name']+"\n")
=======
                    add = input("Press [Enter] to stop adding rules for an event")
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                    if add:
                        count += 1
                        name = "R"+str(count)
                        condition_id = self.define_condition(event,"C"+str(count))
                        action_id = self.define_action()
                        rule_ids.append(self.dbs.add_to_database("Rules", {"workflow_id": self.id, "event": event_id,
                                                                           "condition": condition_id, "name": name,
                                                                           "action": action_id}))
                    else:
                        break
                self.dbs.update_record("Events", {"_id": event_id}, {"rules": rule_ids})

    def define_condition(self, event, name):

<<<<<<< HEAD
        global_vars = self.dbs.find_one_record("Globals", {"workflow_id": self.id})['globals']
        for glob in global_vars:
=======
        for glob in self.globals:
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
            print(glob)
        for param in event['affected_objects']:
            print(param)

<<<<<<< HEAD
        operand = input("choose as operand, global constants or input params\n")
        operator = input("Enter the operator\n")
        constant = input("Enter the constant\n")
=======
        operand = input("choose as operand, global constants or input params")
        operator = input("Enter the operator")
        constant = input("Enter the constant")
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
        condition = {'workflow_id': self.id, 'name': name, 'operand': operand,
                     'operator': operator, 'constant': constant}

        return self.dbs.add_to_database("Conditions", condition)

    def define_action(self):
<<<<<<< HEAD
        name = input("Enter the name of the action\n").upper()
        handler = input("Enter the module, class, function with a .\n")
        affected_objects = self.choose_affected_objects()
        ids = list()
        while True:
            add = input("press [Enter] to stop adding raised events\n")
            if add:
                for event in self._events:
                    print(event['name'])
                event = input("Enter the name of the event\n").upper()
                event_id = self.dbs.find_one_record("Events", {"workflow_id": self.id, "name": event})['_id']
=======
        name = input("Enter the name of the action").upper()
        handler = input("Enter the module, class, function with a .")
        affected_objects = self.choose_affected_objects()
        ids = list()
        while True:
            add = input("press [Enter] to stop adding raised events")
            if add:
                for event in self._events:
                    print(event['name'])
                event = input("Enter the name of the event").upper()
                event_id = self.dbs.find_one_record("Events", {"workflow_id": self.id, "name": event})
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                ids.append(event_id)
            else:
                break
        return self.dbs.add_to_database("Actions", {"workflow_id": self.id, "name": name,
                                                    "handler": handler, "raised_events": ids,
                                                    "affected_objects": affected_objects})

    def choose_affected_objects(self, l=None):
        ao = list()
        if l:
            while True:
<<<<<<< HEAD
                add = input("Enter affected objects from this list\n"+str(l)+'\n')
=======
                add = input("Enter affected objects from this list\n"+str(l))
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
                if add:
                    ao.append(input().upper())
                else:
                    break
            return ao
        while True:
<<<<<<< HEAD
            add = input("Enter affected objects\n")
=======
            add = input("Enter affected objects")
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
            if add:
                ao.append(input().upper())
            else:
                break
        return ao

    def _get_tasks(self, tasks):
        t = list()
        for task in tasks:
            t_data = dict()
            for key, value in task.items():
                if key != "_id":
                    t_data[key] = value
            t.append(t_data)
        return t

    def _get_events(self, events):
        event_list = list()
        for event in events:
            event_data = dict()
            event_data['name'] = event['name']
            event_data['affected_objects'] = event['affected_objects']
            rules = self.dbs.find_many_records("Rules", {'workflow_id': self.id})
            rls = list()
            for rule in rules:
                rls.append(self.dbs.find_one_record("Rules", rule)['name'])
            event_data['rules'] = rls
            event_list.append(event_data)
        return event_list

    def _get_rules(self, rules):
        rule_list = list()
        for rule in rules:
            rdata = dict()
            rdata['name'] = rule['name']
            rdata['action'] = self.dbs.find_one_record("Actions", {'_id': rule['action']})['name']
            rdata['condition'] = self.dbs.find_one_record("Conditions", {'_id': rule['condition']})['name']
            rule_list.append(rdata)
        return rule_list

    def _get_actions(self, actions):
        action_list = list()
        for action in actions:
            a_data = dict()
            a_data['name'] = action['name']
            a_data['handler'] = action['handler']
            a_data['affected_objects'] = action['affected_objects']
            a_data['raised_events'] = list()
            for re in action['raised_events']:
                a_data['raised_events'].append(self.dbs.find_one_record("Events", {'_id': re})['name'])
            action_list.append(action)
        return action_list

    def _get_conditions(self, conditions):
        conditions_list = list()
        for condition in conditions:
            c_data = dict()
            c_data['operand'] = condition['operand']
            c_data['operand'] = condition['operand']
            c_data['operand'] = condition['operand']
            c_data['name'] = condition['name']
            conditions_list.append(c_data)
        return conditions_list

    def store(self):
        data = dict()
        tasks = self.dbs.find_many_records("Tasks", {"workflow_id": self.id})
        data['tasks'] = self._get_tasks(tasks)

        events = self.dbs.find_many_records("Events", {"workflow_id": self.id})
        data['events'] = self._get_events(events)

        rules = self.dbs.find_many_records("Rules", {'workflow_id': self.id})
        data['rules'] = self._get_rules(rules)

        actions = self.dbs.find_many_records("Actions", {"workflow_id": self.id})
        data['actions'] = self._get_actions(actions)

        conditions = self.dbs.find_many_records("Conditions", {"workflow_id": self.id})
        data['conditions'] = self._get_conditions(conditions)

        data['resources'] = self.dbs.find_one_record("Resources", {"workflow_id": self.id})
        data['roles'] = self.dbs.find_one_record("Roles", {"workflow_id": self.id})
<<<<<<< HEAD
        data['globals'] = self.dbs.find_one_record("Globals", {"workflow_id": self.id})
=======
        data['globals'] = self.dbs.find_one_record("Globals", {"workflow_id", self.id})
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
        data['constants'] = self.dbs.find_one_record("Constants", {"workflow_id": self.id})

        data['title'] = self.title
        data['description'] = self.description
        data['type'] = self.type

        return data

<<<<<<< HEAD
=======

>>>>>>> fb78d41550d471ef727838696ff62068320965e6
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
        pp_json(json_dict_or_string, f)


<<<<<<< HEAD
# if __name__ == "__main__":
#     print("Testing workflow module!")
#     f_name = input("Input a file name\n")
#     if not len(f_name):
#         print("Input file not found. Let's start specifying a workflow\n")
#         Workflow()
=======
if __name__ == "__main__":
    print("Testing workflow module!")
    f_name = input("Input a file name")
    if not len(f_name):
        print("Input file not found. Let's start specifying a workflow")
        w = Workflow()
>>>>>>> fb78d41550d471ef727838696ff62068320965e6
