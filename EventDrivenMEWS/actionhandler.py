from states import TaskStates
import database_funcs


class ActionHandler:

    def __init__(self,eh):
        self.eventhandler = eh
        self.dbf = database_funcs.Database()

    def add_to_worklist(self,task):
        #add task to the worklist of the owner of the task
        record = {'role': task.handler}
        user = self.dbf.find_one_record("Users", record)
        record = {'name':user['name'],'password':user['password'], 'role': user['role'], 'task': task.id}
        self.dbf.add_to_database("Worklist", record)

    def get_response(self, task):
        record = {"user":task.handler, "task_id": task.id}
        while True:
            if not self.dbf.find_one_record("Response", record):
                continue
            return  self.dbf.find_one_record("Response", record)

    def update_to_local_db(self, var, task_id):
        record = {'type':'local', 'task_id': task_id, 'output':var}
        self.dbf.add_to_database("Data", record)


    def update_to_global_db(self, task_data):

        for k, v in task_data.items():
            if k.lower() == 'output':
                continue
            else:
                record = {"type":"global", 'variable':k, 'output': v}
                self.dbf.update_record("Data", record)

    def find_in_global(self, var):
        record = {"type":'global','variable':var}
        try:
            return self.dbf.find_one_record("Data",record)
        except:
            print("Record not found for global variable", var)

    def find_in_local(self, var):
        record = {"type":'global','variable':var}
        try:
            return self.dbf.find_one_record("Data",record)
        except:
            print("Record not found for global variable", var)


    def evaluate_condition(self, condition):
        operand = condition.operand
        operator = condition.operator
        constant = condition.constant

        if operand['type'] == 'global':
            op_val = self.find_in_global(operand)
            return eval(op_val + operator + constant)
        else:
            op_val = self.find_in_local(operand)
            return eval(op_val + operator + constant)


    def execute(self,action,*args, **kwargs):

        assert action.task is not None
        task = action.task
        task.state = TaskStates.READY

        g_arg, l_arg = task.affected_objects['global'], task.affected_objects['local']
        if task.type == 'manual':
            self.add_to_worklist(task)
            task.state = TaskStates.RUNNING
            task.data = self.get_response(task)

        else:

            mod,cls,func = task.handler
            cls = __import__(mod,cls)
            task.state = TaskStates.RUNNING
            callback = getattr(cls,func)
            task.data = callback(g_arg + l_arg, *args, **kwargs)

        self.update_to_local_db(task.data['output'], task.id) #update new local variables defined in the function
        self.update_to_global_db(task.data)

        task.state = TaskStates.FINISHED
        output_tasks = action.task.output_tasks
        for task in output_tasks:
            event = task['event']
            conditions = task['conditions']
            if self.evaluate_condition(conditions):
                self.eventhandler.add_event(event)
                self.eventhandler.register_action(event, event.task.action)
