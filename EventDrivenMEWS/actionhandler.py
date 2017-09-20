from states import TaskStates
import database_funcs


class ActionHandler:

    def __init__(self,eh):
        self.eventhandler = eh
        self.dbf = database_funcs.Database()

    def add_to_worklist(self,action, role, wid):
        #add task to the worklist of the owner of the task
        record = {'role': role}
        user = self.dbf.find_one_record("Users", record)
        record = {'name':user['name'],'password':user['password'], 'role': user['role'], 'action': action['_id'], "workflow_id":wid}
        self.dbf.add_to_database("Worklist", record)

    def get_response(self, action, user, wid):
        record = {"user":user, "action": action, "workflow_id":wid}
        while True:
            if not self.dbf.find_one_record("Response", record):
                continue
            return  self.dbf.find_one_record("Response", record)

    def add_to_local_db(self, data, task_id, wid):
        if not data or len(data.keys()) == 0:
            return
        for var, value in data.items():
            record = {'type':'local', 'task_id': task_id, 'variable':var, "value": value, "workflow_id":wid}
            self.dbf.add_to_database("Data", record)

    def add_to_global_db(self, task_data, wid):

        if not task_data or len(task_data.keys()) == 0:
            return

        for k,v in task_data.items():
            newrecord = {"type":"global", 'variable':k,'value': v, "workflow_id":wid}
            self.dbf.add_to_database("Data",newrecord)

    def find_in_global(self, var, wid):
        record = {"type":'global','variable':var, "workflow_id":wid}
        try:
            x = self.dbf.find_one_record("Data",record)
            # print("Xis", x)
            return x['value']
        except:
            print("Record not found for global variable", var)

    def find_in_local(self, var, tid, wid):
        record = {"type":'local','variable':var, "task_id": tid,  "workflow_id":wid}
        try:
            return self.dbf.find_one_record("Data",record)['value']
        except:
            print("Record not found for local variable", var)

    def evaluate_condition(self, condition):
        if not condition:
            return True

        wid = condition['workflow_id']
        operand = condition['operand']
        operator = condition['operator']
        constant = condition['constant']

        if operand['type'] == 'global':
            op_val = self.find_in_global(operand, wid)
            return eval(op_val + operator + constant)
        else:
            exp = operand['expression']
            t_name = exp['name']
            var = exp['variable']
            op_val = self.find_in_local(var, t_name, wid)
            return eval(op_val + operator + constant)

    def update_task_state(self, act_or_eve, value):
        wid = act_or_eve['workflow_id']
        name = act_or_eve['task']
        task = self.dbf.find_one_record("Tasks", {"workflow_id": wid, 'name': name})
        temp = task
        task['state'] = value
        self.dbf.update_record("Tasks", temp, task)
        return task

    def get_conditions(self, cids):
        conditions = []
        for c in cids:
            r = self.dbf.find_one_record("conditions", {'_id':c})
            conditions.append(r)

        return conditions

    def update_global(self, global_vars, data, wid):
        print(data)
        # print("Updating global variables", global_vars)
        for var in global_vars:
            var = var[0]
            # print("variable is", var)
            old = self.find_in_global(var, wid)
            new = {"value": data[var]}
            # print("Value is", data[var])
            self.dbf.update_record("Data",{"workflow_id":wid, "variable": var}, new)

    def my_import(self, name):
        __import__(name.rsplit('.', 1)[0])
        components = name.split('.')
        print(components)
        mod = __import__(components[0])
        print(mod)
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    def execute_task(self, handler, *args, **kwargs):
        # print(handler)
        x = handler.rsplit('.', 1)
        cls, func = self.my_import(x[0])(), x[1]
        callback = getattr(cls, func)
        # print("Execution begins!")
        return callback(*args, **kwargs) or None


    def execute(self,action, *args, **kwargs):

        assert action is not None
        action = self.dbf.find_one_record("Actions",{'_id':action})
        print("Action is ", action['Description'])
        task = self.update_task_state(action, TaskStates.READY.value)
        wid = action['workflow_id']
        print(task)

        if task['manual'] == "True":
            print("Adding task to worklist of ", task['owner'])
            self.add_to_worklist(action, task['owner'], wid)

        else:
            for arg in task['affected_objects']['global']:
                for argument in arg:
                    val = self.find_in_global(argument, wid)
                    kwargs[argument] = val
                    # print("global", argument, val)

            for arg in task['affected_objects']['local']:
                t_id = arg[0]
                for var in arg[1]:
                    val = self.find_in_local(var, t_id, wid)
                    kwargs[var] = val
                    # print("local", var, val)

            handler = task['handler']
            task = self.update_task_state(action, TaskStates.RUNNING.value)

            # task['data'] =  #output as the output variable of every task
            task['data'] = self.execute_task(handler, *args, **kwargs)

        self.add_to_local_db(task['data'], task['id'], wid) #update new local variables defined in the function

        self.update_global(task['affected_objects']['global'], kwargs, wid)

        task = self.update_task_state(action, TaskStates.FINISHED.value)
        self.eventhandler.remove_event(self.dbf.find_one_record("Events",{"_id":task['event']}))

        for event in action['output_events']:
            event = self.dbf.find_one_record("Events", {'_id':event})
            c_ids = event['conditions']
            conditions = self.get_conditions(c_ids)
            found = False
            for condition in conditions:
                # print("Condition is", condition)
                if self.evaluate_condition(condition):
                    continue
                else:
                    found = True

            if not found:
                # print(event)
                self.eventhandler.add_event(event)
                action_id = self.dbf.find_one_record("Tasks", {"event": event['_id'], "workflow_id": wid})['action']
                action = self.dbf.find_one_record("Actions", {'_id': action_id})
                print("Registering ",event['Description'], action["Description"])
                self.eventhandler.register_action(action)