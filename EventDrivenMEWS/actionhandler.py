from states import TaskStates
import database_funcs
import operator


class ActionHandler:

    def __init__(self,eh):
        self.ops = {
            '<': operator.lt,
            '<=': operator.le,
            '==': operator.eq,
            '!=': operator.ne,
            '>=': operator.ge,
            '>': operator.gt
        }
        self.eventhandler = eh
        self.dbf = database_funcs.Database()

    def add_to_worklist(self,action, role, wid):

        record = {'role': role}
        user = self.dbf.find_one_record("Users", record)['_id']
        record = {"user_id": user, 'action': action['_id'], "workflow_id":wid}
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
            record = {'type':'local', 'task_id': task_id, 'variable':var, "workflow_id":wid}
            d = self.dbf.find_one_record("Data", record)
            if not d:
                record["value"] = value
                self.dbf.add_to_database("Data", record)
            else:
                self.dbf.update_record("Data", record, {"value": value})

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

    def cmp(self, arg1, op, arg2):
        operation = self.ops.get(op)
        return operation(arg1, arg2)

    def evaluate_condition(self, condition):
        # print("Evaluating",condition)
        wid = condition['workflow_id']
        condition_expr = condition['expression']
        if not condition:
            return True

        operand = condition_expr['operand']
        operator = condition_expr['operator']
        constant = condition_expr['constant']

        if operand['type'] == 'global':
            return True
            op_val = self.find_in_global(operand['variable'], wid)
            return self.cmp(op_val ,operator , constant)
        else:
            exp = operand['expression']
            t_name = exp['name']
            var = exp['variable']
            op_val = self.find_in_local(var, t_name, wid)
            if op_val == None:
                return True
            if type(op_val) == bool:
                op_val = str(op_val)
            # if op_val == "True" or op_val == "False":
            #     op_val = bool(op_val)

            # if constant == "True" or constant == "False":
            #     constant = bool(constant)
            print(op_val, operator, constant)
            # if not op_val:
            #     return True   #For the cases when the task is not yet executed but is a previous task of the task whose event is being evaluated
            return self.cmp(op_val,operator,constant)

    def update_task_state(self, act_or_eve, value):
        print("Updating task state to ", value)
        wid = act_or_eve['workflow_id']
        name = act_or_eve['task']
        self.dbf.update_record("Data",{"workflow_id":wid,"task_id":name, "type":"local", "variable":"state"},{"value":value.lower()})
        task = self.dbf.find_one_record("Tasks", {"workflow_id": wid, 'name': name})
        return task

    def get_conditions(self, cids):
        conditions = []
        for task_c in cids:
            for c in task_c:
                r = self.dbf.find_one_record("conditions", {'_id':c})
                conditions.append(r)

        return conditions

    def update_global(self, global_vars, data, wid):
        # print(data)
        # print("Updating global variables", global_vars)
        for var in global_vars:
            var = var[0]
            if not len(var):
                continue

            old = self.find_in_global(var, wid)
            new = {"value": data[var]}

            self.dbf.update_record("Data",{"workflow_id":wid, "variable": var}, new)

    def my_import(self, name):
        __import__(name.rsplit('.', 1)[0])
        components = name.split('.')
        mod = __import__(components[0])
        print(mod)
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    def execute_task(self, handler, *args, **kwargs):

        x = handler.rsplit('.', 1)
        cls, func = self.my_import(x[0])(*args, **kwargs), x[1]
        callback = getattr(cls, func)

        d = dict()
        d['output'] = callback(*args, **kwargs) or None
        return d


    def execute(self,action, *args, **kwargs):
        print("kwargs:", kwargs)
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

        for event in action['output_events']:
            event = self.dbf.find_one_record("Events", {'_id':event})
            print("Trying to raise events for", event['Description'])
            c_ids = event['conditions']
            conditions = self.get_conditions(c_ids)
            found = False
            condition_type = event['condition_type']
            c = False
            for condition in conditions:
                print("Condition is", condition['expression'])
                if self.evaluate_condition(condition):
                    print("Condition true")
                    if condition['expression']['operand']['type'] == "local" and\
                                    condition['expression']['constant'] == "finished" and condition_type == "or":
                        break
                else:
                    print("Here")
                    found = True

            if not found or c:
                self.eventhandler.add_event(event)
