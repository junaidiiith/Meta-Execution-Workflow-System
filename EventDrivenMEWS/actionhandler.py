from states import TaskStates
import database_funcs


class ActionHandler:

    def __init__(self,eh):
        self.eventhandler = eh
        self.dbf = database_funcs.Database()

    def add_to_worklist(self,task, wid):
        #add task to the worklist of the owner of the task
        record = {'role': task.owner}
        user = self.dbf.find_one_record("Users", record)
        record = {'name':user['name'],'password':user['password'], 'role': user['role'], 'task': task.id, "workflow_id":wid}
        self.dbf.add_to_database("Worklist", record)

    def get_response(self, task, wid):
        record = {"user":task.handler, "task_id": task.id, "workflow_id":wid}
        while True:
            if not self.dbf.find_one_record("Response", record):
                continue
            return  self.dbf.find_one_record("Response", record)

    def add_to_local_db(self, data, task_id, wid):
        for var, value in data.items():
            record = {'type':'local', 'task_id': task_id, 'variable':var, "value": value, "workflow_id":wid}
            self.dbf.add_to_database("Data", record)


    def add_to_global_db(self, task_data, wid):

        for k,v in task_data.items():
            newrecord = {"type":"global", 'variable':k,'output': v, "workflow_id":wid}
            self.dbf.add_to_database("Data",newrecord)

    def find_in_global(self, var, wid):
        record = {"type":'global','variable':var, "workflow_id":wid}
        try:
            return self.dbf.find_one_record("Data",record)
        except:
            print("Record not found for global variable", var)

    def find_in_local(self, var, tid, wid):
        record = {"type":'global','variable':var, "task_id": tid,  "workflow_id":wid}
        try:
            return self.dbf.find_one_record("Data",record)
        except:
            print("Record not found for global variable", var)


    def evaluate_condition(self, condition):
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


    def execute(self,action,*args, **kwargs):

        assert action is not None

        task = self.update_task_state(action, TaskStates.READY.value)
        wid = task['workflow_id']
        for arg in task['affected_objects']['global']:
            val = self.find_in_global(arg,wid)
            kwargs[arg] = val

        for arg in task.affected_objects['local']:
            t_id = arg[0]
            for var in arg[1]:
                val = self.find_in_local(var, t_id, wid)
                kwargs[var] = val

        if task['manual']:
            self.add_to_worklist(task, wid)
            task.state = TaskStates.RUNNING.value
            task.data = self.get_response(task, wid)

        else:
            mod,cls,func = task['handler']
            cls = __import__(mod,cls)
            task = self.update_task_state(action, TaskStates.RUNNING.value)
            callback = getattr(cls,func)
            task.data = callback(*args, **kwargs)

        self.add_to_local_db(task['data'], task['id'], wid) #update new local variables defined in the function
        self.add_to_global_db(task['data'], wid)

        task = self.update_task_state(action, TaskStates.FINISHED.value)
        output_tasks = task['output_tasks']
        for task in output_tasks:
            event = self.dbf.find_one_record("Event", {'_id':task['event']})
            c_ids = event['conditions']
            conditions = self.get_conditions(c_ids)
            for condition in conditions:
                if self.evaluate_condition(condition):
                    self.eventhandler.add_event(event)
                    action = self.dbf.find_one_record("Actions", {'task':task['name'], "workflow_id": wid})
                    self.eventhandler.register_action(event, action)