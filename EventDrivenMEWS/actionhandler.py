from states import TaskStates
import database_funcs
import operator
import sys


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
        record = {"user_id": user, 'action': action['_id'], "workflow_id": wid}
        self.dbf.add_to_database("Worklist", record)

    def get_response(self, action, user, wid):
        record = {"user":user, "action": action, "workflow_id":wid}
        while True:
            if not self.dbf.find_one_record("Response", record):
                continue
            return  self.dbf.find_one_record("Response", record)

    def update_local(self, task_data, local_vars, task_id, wid):
        if not task_data or len(task_data.keys()) == 0:
            return
        # print("Local vars", local_vars)
        for var in local_vars:
            record = {'type':'local', 'task': task_id, 'variable':var, "workflow_id": wid}
            d = self.dbf.find_one_record("Exec_data", record)
            if not d:
                record["value"] = task_data[var]
                # print("Adding record", record)
                self.dbf.add_to_database("Exec_data", record)
            else:
                self.dbf.update_record("Exec_data", record, {"value": task_data[var]})

    def update_global(self, task_data, global_objects, wid):

        if not task_data or len(task_data.keys()) == 0:
            return
        print("Updating ",global_objects,"to ",task_data)
        for obj in global_objects:
            newrecord = {"type": "global", "variable": obj, "workflow_id":wid}
            d = self.dbf.find_one_record("Exec_data", newrecord)
            if not d:
                newrecord['value'] = task_data[obj]
                self.dbf.add_to_database("Exec_data",newrecord)
                # print("Added ", self.dbf.find_one_record("Exec_data", newrecord))
            else:
                self.dbf.update_record("Exec_data",newrecord,{"value": task_data[obj]})

    def find_global(self, var, wid):
        # print("Trying to find global variable", var)
        record = {"type":'global','variable':var, "workflow_id": wid}
        try:
            x = self.dbf.find_one_record("Exec_data", record)
            return x['value']
        except:
            print("Record not found for global variable", var)
            return None

    def find_local(self, var, tid, wid):
        record = {"type":'local','variable':var, "task": tid,  "workflow_id":wid}
        try:
            return self.dbf.find_one_record("Exec_data",record)['value']
        except:
            print("Record not found for local variable", var, " for task ", tid)
            return None

    def get_global_vars(self, task):
        if task['data']:
            global_vars = task['affected_objects']['global']
            return list(set(task['data'].keys()).intersection(set(global_vars)))
        return None

    def get_local_vars(self, task):
        if task['data']:
            data = list(task['data'].keys())
            if "ueh" in data:
                data.remove("ueh")
            if "uw" in data:
                data.remove("uw")

            global_vars = task['affected_objects']['global']
            local_vars = list(set(data) - set(global_vars))
            # print(global_vars,data, local_vars)
            return local_vars
        return None

    def cmp(self, arg1, op, arg2):
        operation = self.ops.get(op)
        return operation(arg1, arg2)

    def evaluate_condition(self, condition):
        print("Evaluating",condition['expression'])
        wid = condition['workflow_id']
        condition_expr = condition['expression']
        if not condition:
            return True

        operand = condition_expr['operand']
        operator = condition_expr['operator']
        constant = condition_expr['constant']
        if operand['type'] == 'global':
            # return True
            op_val = self.find_global(operand['variable'], wid)
            print("Checking global condition...")
            if self.cmp(op_val, operator, constant):
                print("Condition is true")
                return  True
            else:
                print("Condition is false")
                return False
        else:
            print("Checking local condition...")
            exp = operand['task']
            t_name = exp['name']
            var = exp['variable']
            op_val = self.find_local(var, t_name, wid)
            # print("Operator value is", op_val)
            if op_val is None:
                print("True condition")
                return True
            if type(op_val) != str:
                op_val = str(op_val)

            if self.cmp(op_val,operator,constant):
                print("Condition true")
                return True
            print("Condition false")
            return False

    def update_task_state(self, act_or_eve, value):
        print("Updating task state to ", value)
        task = self.dbf.find_one_record("Tasks", {"action": act_or_eve['_id']})
        wid = act_or_eve['workflow_id']
        name = act_or_eve['task']
        # if task['type'] == "user":
        #     print("Updating state for ", name)
        #     print({"workflow_id": wid, "task_id": name, "type": "local", "variable": "state"})
        self.dbf.update_record("Exec_data",{"workflow_id": wid,"task": name,
                                            "type":"local", "variable":"state"},{"value":value})

        return task

    def get_conditions(self, cids):
        conditions = []
        for cid in cids:
            r = self.dbf.find_one_record("conditions", {'_id': cid})
            conditions.append(r)

        return conditions

    def my_import(self, name):
        __import__(name.rsplit('.', 1)[0])
        components = name.split('.')
        mod = __import__(components[0])
        # print(mod)
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    def execute_task(self, handler, *args, **kwargs):

        cls, func = self.my_import(handler[0]+'.'+handler[1])(*args, **kwargs), handler[-1]
        callback = getattr(cls, func)

        d = callback(*args, **kwargs) or None
        return d

    def wait_till_complete(self, action):

        tname = self.dbf.find_one_record("Tasks",{"action": action['_id']})['name']
        record = {"workflow_id": action['workflow_id'], "type": "local", "variable": "state",
                                           "value": "finished", "task":tname }
        output = self.dbf.find_one_record("Exec_data",
                                          record)
        # print("Output is", output)
        print("Waiting for agent to respond....")
        while not output:
            # print("Output is", output)
            output = self.dbf.find_one_record("Exec_data",
                                              record)
            # print("Output is", output)

    def execute(self,action, *args, **kwargs):
        # print("kwargs:", kwargs)
        assert action is not None

        action = self.dbf.find_one_record("Actions", {'_id': action})
        task = self.update_task_state(action, TaskStates.READY.value)

        wid = action['workflow_id']
        # print(task)

        if task['manual'] == "True":
            print("Adding task to worklist of ", task['owner'])
            # print("Action is", action)
            self.add_to_worklist(action, task['owner'], wid)
            self.wait_till_complete(action)
        else:
            # print("In local!!")
            if task['type'] == 'user':
                print("--User task execution--", task['name'])

            for argument in task['affected_objects']['global']:
                print("-------------Finding global variables values-------------")
                print(argument)
                val = self.find_global(argument, wid)
                kwargs[argument] = val
                # print("global", argument, val)

            local_argument_list = []

            for local_affects in task['affected_objects']['local']:
                key = list(local_affects.keys())[0]
                vals = local_affects[key]
                for val in vals:
                    if self.find_local(val, key, wid) is not None:
                        value = self.find_local(val, key, wid)
                        local_argument_list.append(value)

            # print("local arguement list", local_argument_list)
            handler = task['handler']
            task = self.update_task_state(action, TaskStates.RUNNING.value)

            # task['data'] =  #output as the output variable of every task
            # print("Data before", kwargs)
            print("Executing", task['name'])
            task['data'] = self.execute_task(handler, *local_argument_list, **kwargs)
            print("Data after", task['data'])

        self.update_local(task['data'],self.get_local_vars(task), task['name'], wid) #update new local variables defined in the function
        self.update_global(task['data'], self.get_global_vars(task), wid) #update global variables

        # print("Updating task state of", task['name'], ' to finished')
        task = self.update_task_state(action, TaskStates.FINISHED.value)

        out_events = action['output_events']
        # print(action)
        # print("Output events of ",task['name'],out_events)
        if len(out_events) > 1:
            # print("Multiple and condition case")
            for event in out_events:
                event = self.dbf.find_one_record("Events", {'_id': event})
                # print("Trying to raise events for", event['Description'])
                c_ids = event['conditions']
                # print(c_ids)
                conditions = self.get_conditions(c_ids)
                found = True
                for condition in conditions:
                    if not self.evaluate_condition(condition):
                        found = False
                if found:
                    self.eventhandler.add_event(event)
                    # print("Adding state variable to", event['task'])
                    record = {'workflow_id': wid, "type": "local",
                              "variable": "state", "value": "not started", "task": event['task']}
                    self.dbf.add_to_database("Exec_data", record)
                    # print("Added ", self.dbf.find_one_record("Exec_data", record))
        elif len(out_events) == 1:
            # print("Simple xor or series condition case!")
            event = self.dbf.find_one_record("Events",{"_id":out_events[0]})
            if task['type'] == 'user':
                print("Trying to raise events for", event['Description'])
            c_ids = event['conditions']
            conditions = self.get_conditions(c_ids)
            found = False
            for condition in conditions:
                # print("condition:",condition['expression']['operand'])
                operand = condition['expression']['operand']
                if not self.evaluate_condition(condition):
                    found = True
                    print("Unexpected condition.....")
            if not found:
                self.eventhandler.add_event(event)
            # print("Adding state variable to", task)
                record = {'workflow_id': wid, "type": "local",
                                                   "variable": "state", "value": "not started", "task": event['task']}
                self.dbf.add_to_database("Exec_data", record)
            # print("Added ", self.dbf.find_one_record("Exec_data",record))


