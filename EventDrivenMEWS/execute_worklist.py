from database_funcs import Database
from states import TaskStates


class WorklistExecution:
    def __init__(self):
        self.actions = []
        self.user = input("Enter your name")
        self.password = input("Enter password")
        self.dbs = Database()
        user = self.find_user()
        while not user:
            self.user = input("Invalid credentials.\nEnter your name")
            self.password = input("Enter your password")
            user = self.find_user()
        self.worklist = [record['action'] for record in self.get_worklist()]
        if not self.worklist:
            print("No tasks pending!")
        else:
            self.execute_worklist()
        self.actions = []

    def find_user(self):
        record = {'name':self.user, 'password':self.password}
        try:
            return self.dbs.find_one_record('Users', record)['_id']
        except:
            return None

    def get_worklist(self):
        record = {'name':self.user, 'password':self.password}
        user_id = self.dbs.find_one_record("Users",record)['_id']
        return self.dbs.find_many_records("Worklist", {"user_id":user_id})


    def print_tasks(self):
        worklist = self.worklist
        i = 1
        for w in worklist:
            action = self.dbs.find_one_record("Actions", {'_id': w})
            self.actions.append(action['_id'])
            print(str(i)+')',action['Description'])
            i += 1

    def get_task(self, action):
        record = {"action":action}
        return self.dbs.find_one_record("Tasks", record)

    def add_to_local_db(self, data, task_id, wid):
        for var, value in data.items():
            record = {'type':'local', 'task_id': task_id, 'variable':var, "value": value, "workflow_id":wid}
            self.dbs.add_to_database("Data", record)

    def add_to_global_db(self, task_data, wid):

        for k,v in task_data.items():
            newrecord = {"type":"global", 'variable':k,'output': v, "workflow_id":wid}
            self.dbs.add_to_database("Data",newrecord)

    def find_in_global(self, var, wid):

        record = {"type":'global','variable':var, "workflow_id":wid}
        try:
            x = self.dbs.find_one_record("Data",record)
            # print("Xis", x)
            return x['value']
        except:
            print("Record not found for global variable", var)

    def find_in_local(self, var, tid, wid):
        record = {"type":'local','variable':var, "task_id": tid,  "workflow_id":wid}
        try:
            return self.dbs.find_one_record("Data",record)['value']
        except:
            print("Record not found for local variable", var, " for task ", tid)

    def update_task_state(self, act_or_eve, value):
        # print("action is",act_or_eve)
        action = self.dbs.find_one_record("Actions", {"_id": act_or_eve})
        wid = action['workflow_id']
        name = action['task']
        oldrecord = {"workflow_id":wid,"task_id":name, "type":"local",
                                       "variable":"state"}
        newrecord = {"value":value.lower()}
        print("Changing state for", oldrecord, " to ", newrecord)
        self.dbs.update_record("Data",oldrecord, newrecord)


    def my_import(self, name):
        __import__(name.rsplit('.', 1)[0])
        components = name.split('.')
        mod = __import__(components[0])
        # print(mod)
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

    def execute_worklist(self, *args, **kwargs):
        self.print_tasks()
        action_no = input("Choose which action to perform")
        while action_no and int(action_no) <= len(self.worklist):
            print("Executing action", action_no)
            action = self.actions[int(action_no)-1]
            self.worklist.remove(action)
            task = self.get_task(action)
            wid = task['workflow_id']

            for arg in task['affected_objects']['global']:
                arg = arg[0]
                val = self.find_in_global(arg, wid)
                kwargs[arg] = val

            for arg in task['affected_objects']['local']:
                t_id = arg[0]
                for var in arg[1]:
                    val = self.find_in_local(var, t_id, wid)
                    kwargs[var] = val


            task['data'] = self.execute_task(task['handler'], *args, **kwargs)

            self.add_to_local_db(task['data'], task['name'], wid)  # update new local variables defined in the function
            self.add_to_global_db(task['data'], wid)

            self.update_task_state(action, TaskStates.FINISHED.value)

            if not len(self.worklist):
                print("No tasks pending!!")
                break
            action_no = input("Choose the next action to perform")