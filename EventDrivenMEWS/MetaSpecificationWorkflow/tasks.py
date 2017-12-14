from database_funcs import Database
import sys
import json
import task
from uuid import uuid4


def get_expression():
    type = input("Choose 1) Global 2) Task output variable")
    if type == "1":
        operand = {"type": 'global', 'variable': input("Enter the variable name for comparison")}
    else:
        name = input("Enter the task name")
        variable = input("Enter the variable name for comparison")
        operand = {'type': 'local', 'expression': {'name': name, 'variable': variable}}

    operator = input("Enter the operator")
    constant = input("Enter the constant to compare")
    return {'operand': operand, 'operator': operator, 'constant': constant}


class Tasks:
    def __init__(self, *args, **kwargs):
        self.type = "user"

    def start(self, *args, **kwargs):
        print("Initiating workflow exec")
        kwargs['user_workflow_id'] = str(uuid4())
        kwargs['state'] = "started"
        d = Database()
        d.add_to_database("Workflow",{'id':kwargs['user_workflow_id']})
        kwargs['output'] = True
        return kwargs

    def basic_workflow_definition(self, *args, **kwargs):
        wid = kwargs['user_workflow_id']
        print("bwd wid is", wid)
        d = Database()
        data = dict()
        data['id'] = wid
        data['title'] = input("Enter the title of the workflow")
        data['definition'] = input("Enter the workflow definition")
        data['description'] = input("Enter the description of the workflow")
        kwargs['output'] = True
        d.update_record("Workflow",{"id":wid}, data)
        return kwargs

    def define_roles(self, *args, **kwargs):
        wid = kwargs['user_workflow_id']
        print("dr wid is", wid)

        d = Database()
        choice = input("1) Choose a file\n2)Enter roles manually")
        if choice == 1:
            try:
                json_file = open(input("Enter the file name"))
                content = json.loads(json_file.read())['roles']
            except FileNotFoundError:
                sys.exit(0)
        else:
            print("Enter roles. Press [ENTER] to quit adding role")
            content = []
            while True:
                role = input("Enter a role")
                if not role:
                    break
                content.append(role)
        d.update_record("Workflow", {"id": wid}, {"roles": content})
        kwargs['output'] = True
        return kwargs

    def define_resources(self, *args, **kwargs):
        wid = kwargs['user_workflow_id']
        print("dres wid is", wid)

        d = Database()
        choice = input("1)Choose a file\n2)Enter resources manually")
        if choice == 1:
            try:
                json_file = open(input("Enter the file name"))
                content = json.loads(json_file.read())['resources']
            except FileNotFoundError:
                sys.exit(0)
        else:
            print("Enter resources. Press [ENTER] to quit adding resources")
            content = []
            while True:
                resource = input("Enter a resource")
                if not resource:
                    break
                content.append(resource)
        d.update_record("Workflow", {"id": wid}, {"resources": content})
        kwargs['output'] = True
        return kwargs

    def define_tasks(self, *args, **kwargs):
        print("Defining tasks for the workflow")
        wid = kwargs['user_workflow_id']
        print("dt wid is", wid)

        tsk = dict()
        tasks = list()
        d = Database()
        while True:
            t = task.create_task(wid)
            tsk[t.id] = t
            d.add_to_database("Tasks", t.put())
            tasks.append(d.find_one_record("Tasks", t.put()))
            i = input("1: Add task [Enter]: Completed defining tasks")
            if i != "1":
                break
        kwargs["output"] = True
        return kwargs

    def define_sequence(self, *args, **kwargs):
        wid = kwargs['user_workflow_id']
        print("ds wid is", wid)

        d = Database()
        tasks = d.find_many_records("Tasks",{"workflow_id":wid})
        temp = []
        i = 0
        print("These are the tasks. Select the output tasks of each task")
        for tsk in tasks:
            print(i + 1, ")Task name is: ", tsk['name'])
            temp.append(tsk)
            i += 1

        for task in temp:
            i = input("Enter the index of output task of " + task['name'])
            out_events = []
            while len(i):
                tsk = temp[int(i) - 1]
                conditions = []
                c = dict()
                c['type'] = 'Arithmetic'
                c['expression'] = {'operand': {'type': 'local', 'task': {'name': task['name'], 'variable': 'state'}},
                                   'operator': '==', 'constant': 'finished'}
                c['event_id'] = tsk['event']
                c['user_workflow_id'] = wid
                d.add_to_database("conditions", c)
                c_id = d.find_one_record("conditions", c)['_id']
                conditions.append(c_id)
                typ = input("Choose the type of condition\n 1) Arithmetic 2)Database 3) External 4) System")
                while typ:
                    c = dict()
                    exp = get_expression()
                    if exp:
                        c['type'] = typ
                        c['expression'] = exp
                        c['event_id'] = tsk['event']
                        c['workflow_id'] = wid
                        d.add_to_database("conditions", c)
                        c_id = d.find_one_record("conditions", c)['_id']
                    conditions.append(c_id)
                    typ = input("Choose the type of condition\n 1) Arithmetic 2)Database 3) External 4) System."
                                "Press [Enter] to stop adding condition ")

                evnt = d.find_one_record("Events", {'_id': tsk['event']})
                evnt['conditions'] += conditions

                d.update_record("Events", {'_id': tsk['event']}, evnt)
                out_events.append(evnt['_id'])
                print("Task and condition added")
                i = input("press [Enter] to move on to the next task or index of the next output task")

            act = d.find_one_record("Actions", {'_id': task['action']})

            act['output_events'] = out_events
            d.update_record("Actions", {'_id': task['action']}, act)

        record = {"workflow_id": wid}
        events = d.find_many_records("Events", record)
        for event in events:
            print(event['task'])
            typ = input("Enter the type of conditions join/and/or for this task [default 'AND']")
            event['condition_type'] = typ
            d.update_record("Events", {'_id': event['_id']}, event)

        print("Initializing the default values of the constant variables")

        constants = dict()
        while True:
            var_name = input("Enter the name of a constant variable")
            if len(var_name):
                val = input("Enter the default value")
                assert val is not None
                constants[var_name] = val
            else:
                break
        d.update_record("Workflow",{"id":wid},{"constants":constants})
        globals = dict()
        while True:
            var_name = input("Enter the name of a global variable")
            if len(var_name):
                val = input("Enter the default value")
                assert val is not None
                globals[var_name] = val
            else:
                break
        d.update_record("Workflow", {"id": wid}, {"globals":globals})
        kwargs['output'] = True
        return kwargs

    def store_workflow(self, *args, **kwargs):
        wid = kwargs['user_workflow_id']
        print("wid is sw", wid)

        db = Database()
        tasks = db.find_many_records("Tasks",{"workflow_id":wid})
        print("Tasks are", tasks)
        for task in tasks:
            outtasks = []
            action = db.find_one_record("Actions",{'_id': task['action']})
            out_events = action['output_events']
            for event in out_events:
                event_data = db.find_one_record("Events",{'_id':event})
                outtask = event_data['task']
                conditions = event_data['conditions']
                outcond = []
                for condition in conditions:
                    d = dict()
                    cond_data = db.find_one_record("conditions",{'_id':condition})
                    d['expression'] = cond_data['expression']
                    d['type'] = cond_data['type']
                    outcond.append(d)
                outtasks.append({'task':outtask, 'conditions':outcond})
            task['output_tasks'] = outtasks
        tsks = []
        tasks = db.find_many_records("Tasks", {"workflow_id": wid})
        for tsk in tasks:
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

        db.update_record("Workflow",{"id":wid},{"tasks":tsks})
        print(tsks)

        print(db.find_one_record("Workflow",{"id":wid}))


        def pretty_print(json_dict_or_string, f):
            def pp_json(json_dict_or_string, f, sort=True, indents=4):
                fl = open(f, 'w')
                if type(json_dict_or_string) is str:
                    fl.write(json.dumps(json.loads(json_dict_or_string), sort_keys=sort, indent=indents))
                else:
                    fl.write(json.dumps(json_dict_or_string, sort_keys=sort, indent=indents))

            pp_json(json_dict_or_string, f)

        data = db.find_one_record("Workflow",{"id":wid})
        print(data)
        content = dict()
        for key, value in data.items():
            if key == "_id" or key == 'id':
                continue
            content[key] = value
        pretty_print(content, content['title']+'.json')
        print("Your specification workflow json is in", data['title']+'.json')
        print("--------------Specification end----------")

    def end(self):
        print("Done with the execution")