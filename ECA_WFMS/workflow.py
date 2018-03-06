from .mongo_database import Database
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
            self.title = input("Enter the title of the workflow\n")
            self.type = input("Enter the type of the workflow\n")
            self.description = input("Enter the description of the workflow\n")

        self._events = None
        self._rules = None
        self.start = None
        self.define_roles(json_file)
        self.define_resources(json_file)
        self.define_constants(json_file)
        self.define_globals(json_file)
        self.define_tasks(json_file)
        self.define_events(json_file)
        self.define_eca_rules(json_file)
        self.content = self.store()
        self.to_json()
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
                role = input("Enter a role\n")
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
                role = input("Enter a resource\n")
                if not role:
                    break
                resources.append(role)
        self.dbs.add_to_database('Resources', {'resources': resources, 'workflow_id': self.id})

    def define_globals(self, json_file=None):
        print("Initializing the default values of the global variables")
        global_vars = dict()
        if json_file:
            for key, value in json_file['globals'].items():
                global_vars[key] = value
        else:
            global_vars['state'] = "Not started"
            while True:
                var_name = input("Enter the name of a global variable\n")
                if len(var_name):
                    val = input("Enter the default value\n")
                    assert val is not None
                    global_vars[var_name] = val
                else:
                    break
        self.dbs.add_to_database('Globals', {'globals': global_vars, 'workflow_id': self.id})

    def define_constants(self, json_file=None):
        constants = dict()
        print("Initializing the default values of the constant variables")
        if json_file:
            for key, value in json_file['constants'].items():
                constants[key] = value
        else:
            while True:
                var_name = input("Enter the name of a constant variable\n")
                if len(var_name):
                    val = input("Enter the default value\n")
                    assert val is not None
                    constants[var_name] = val
                else:
                    break
        self.dbs.add_to_database('Constants', {'constants': constants, 'workflow_id': self.id})

    def define_tasks(self, json_file=None):
        print("Defining tasks")
        if json_file:
            tasks = json_file['tasks']
            for task in tasks:
                t_data = dict()
                for key, value in task.items():
                    t_data[key] = value
                t_data['workflow_id'] = self.id
                self.dbs.add_to_database("Tasks", t_data)
        else:
            print("Defining tasks for the workflow")

            while True:
                add = input("Press [Enter] to stop adding tasks else any key\n")
                if len(add):
                    task = dict()
                    task['workflow_id'] = self.id
                    task['name'] = input("Enter the name of the task\n")
                    task['description'] = input("Enter the description of the task\n")
                    attribs = ['input_events', 'output_events', 'input_params', 'output_params']
                    for attrib in attribs:
                        l = []
                        while True:
                            add = input("Press [Enter] to stop adding "+attrib+'\n')
                            if add:
                                name = input("Enter the name of "+attrib[:-1]+'\n').upper()
                                l.append(name)
                            else:
                                break
                        task[attrib] = l
                    self.dbs.add_to_database("Tasks", task)
                else:
                    break
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

    def define_events(self, json_file=None):
        event_set = set()
        event_list = list()
        if json_file:
            events = json_file["events"]
            for event in events:
                task = self.dbs.find_one_record("Tasks", {"name": event['task']})
                if event['name'] not in event_set:
                    event_set.add(event['name'])
                    record = {'task_id': task['_id'], 'task_name': task['name'],
                              "name": event['name'], 'description': event['description'],
                              'affected_objects': event['affected_objects'], "workflow_id": self.id}
                    event_list.append(self.dbs.add_to_database("Events", record))
                    if event['name'] == 'START_WORKFLOW':
                        print("Start event found")
                        self.start = event_list[-1]
            self._events = event_list
        else:
            events = list()
            tasks = self.dbs.find_many_records("Tasks", {'workflow_id': self.id})
            for task in tasks:
                if task['name'].lower() == "end":
                    for event in task['output_events']:
                        event_set.add((event, None))

                for event in task['input_events']+task['output_events']:
                    if event not in event_set:
                        event_set.add(event)
                        description = input("Enter the description of the event: "+str(event)+'\n')
                        affected_objects = self.define_affected_objects()
                        record = {'task_id': task['_id'], 'task_name': task['name'], 'workflow_id': self.id,
                                  "affected_objects": affected_objects,
                                  "name": event, 'description': description}
                        events.append(self.dbs.add_to_database("Events", record))
                        if event == "START_WORKFLOW":
                            self.start = event[-1]
            self._events = events
            print("--Events defined--")

    def define_eca_rules(self, json_file=None):
        if json_file:
            rules = json_file['rules']
            assert self._events is not None
            rule_dict = dict()
            for rule in rules:
                event = self.dbs.find_one_record("Events", {"workflow_id": self.id, "name": rule['event']})
                conditions = json_file['conditions']
                for cond in conditions:
                    if cond['name'] == rule['condition']:
                        condition = cond
                        break
                condition['workflow_id'] = self.id
                condition_id = self.dbs.add_to_database("Conditions", condition)
                actions = json_file['actions']
                for act in actions:
                    if act['name'] == rule['action']:
                        action = act
                        break
                raised_events = action['raised_events']
                re_ids = list()

                for re in raised_events:
                    re_ids.append(self.dbs.find_one_record("Events",
                                                               {"workflow_id": self.id, "name": re})['_id'])

                action_id = self.dbs.add_to_database("Actions", {"workflow_id": self.id, "name": action['name'],
                                                                 'handler': action['handler'],
                                                                 'affected_objects': action['affected_objects'],
                                                                 'raised_events': re_ids})

                record = {"workflow_id": self.id,
                          "name": rule['name'],
                          "event": event['_id'],
                          "condition": condition_id, "action": action_id}
                try:
                    rule_dict[event['name']].append(self.dbs.add_to_database("Rules", record))
                except:
                    rule_dict[event['name']] = [self.dbs.add_to_database("Rules", record)]

            for e, rls in rule_dict.items():
                old_event = self.dbs.find_one_record("Events", {"workflow_id": self.id, "name": e})
                new_event = old_event.copy()
                new_event['rules'] = rls
                self.dbs.update_record("Events", old_event, new_event)
        else:
            print("Defining ECA rules")
            count = 0
            for event_id in self._events:
                event = self.dbs.find_one_record("Events", {'_id': event_id})
                rule_ids = list()
                while True:
                    add = input("Press [Enter] to stop adding rules for an event "+event['name']+"\n")
                    if add:
                        count += 1
                        name = "R"+str(count)
                        condition_id = self.define_condition(event, "C"+str(count))
                        action_id = self.define_action()
                        rule_ids.append(self.dbs.add_to_database("Rules", {"workflow_id": self.id, "event": event_id,
                                                                           "condition": condition_id, "name": name,
                                                                           "action": action_id}))
                    else:
                        break
                self.dbs.update_record("Events", {"_id": event_id}, {"rules": rule_ids})
        print("ECA rules defined")

    def define_condition(self, event, name):

        global_vars = self.dbs.find_one_record("Globals", {"workflow_id": self.id})['globals']
        for glob in global_vars:
            print(glob)
        for key, value in event['affected_objects'].items():
            print(key, ":", value)

        op_type = input("choose as operand, global constants or task params[task[space]param name]\n")
        op_type = op_type.strip().split()
        if len(op_type) == 2:
            operand = {"type": "local", "task_name": op_type[0], "variable": op_type[1]}
        else:
            operand = {"type": "global", "variable": op_type[0]}

        operator = input("Enter the operator\n")
        constant = input("Enter the constant\n")
        condition = {'workflow_id': self.id, 'name': name, 'operand': operand,
                     'operator': operator, 'constant': constant}

        return self.dbs.add_to_database("Conditions", condition)

    def define_action(self):
        name = input("Enter the name of the action\n").upper()
        handler = input("Enter the module, class, function with a .\n")
        affected_objects = self.define_affected_objects()
        ids = list()
        while True:
            add = input("press [Enter] to stop adding raised events\n")
            if add:
                es = self.dbs.find_many_records("Events", {'workflow_id': self.id})
                for e in es:
                    print(e['name'])

                event = input("Enter the name of the event\n").upper()
                event_id = self.dbs.find_one_record("Events", {"workflow_id": self.id, "name": event})['_id']
                ids.append(event_id)
            else:
                break

        record = {"workflow_id": self.id, "name": name,
                  "handler": handler, "raised_events": ids,
                  "affected_objects": affected_objects}
        return self.dbs.add_to_database("Actions", record)

    def define_affected_objects(self):
        affected_objects = dict()
        tasks = list()
        ts = self.dbs.find_many_records("Tasks", {'workflow_id': self.id})
        for t in ts:
            tasks.append(t['name'])

        print("Defining local objects for the event from the tasks")
        local = list()
        while True:
            for t in tasks:
                print(t)
            t_name = input("Enter the task name or enter to adding affected objects")
            if t_name:
                ao = input("Enter affected object")
                local.append((t_name, ao))
            else:
                break

        affected_objects['local'] = local
        print("Defining global affected objects")
        g = list()
        while True:
            ao = input("Enter an affected object or [Enter] to stop")
            if len(ao):
                g.append(ao)
            else:
                break
        affected_objects['globals'] = g
        return affected_objects

    def _get_tasks(self, tasks):
        t = list()
        for task in tasks:
            t_data = dict()
            for key, value in task.items():
                if key != "_id" and key != 'workflow_id':
                    t_data[key] = value
            t.append(t_data)
        return t

    def _get_events(self, events):
        event_list = list()
        for event in events:
            event_data = dict()
            event_data['name'] = event['name']
            event_data['affected_objects'] = event['affected_objects']
            event_data['task'] = event['task_name']
            event_data['description'] = event['description']
            rules = event['rules']
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
            rdata['event'] = self.dbs.find_one_record("Events", {'_id': rule['event']})['name']
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
            action_list.append(a_data)
        return action_list

    def _get_conditions(self, conditions):
        conditions_list = list()
        for condition in conditions:
            c_data = dict()
            c_data['operand'] = condition['operand']
            c_data['operator'] = condition['operator']
            c_data['constant'] = condition['constant']
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

        data['resources'] = self.dbs.find_one_record("Resources", {"workflow_id": self.id})['resources']
        data['roles'] = self.dbs.find_one_record("Roles", {"workflow_id": self.id})['roles']
        data['globals'] = self.dbs.find_one_record("Globals", {"workflow_id": self.id})['globals']
        data['constants'] = self.dbs.find_one_record("Constants", {"workflow_id": self.id})['constants']

        data['title'] = self.title
        data['description'] = self.description
        data['type'] = self.type

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
        pp_json(json_dict_or_string, f)


# if __name__ == "__main__":
#     print("Testing workflow module!")
#     f_name = input("Input a file name\n")
#     if not len(f_name):
#         print("Input file not found. Let's start specifying a workflow\n")
#         Workflow()
