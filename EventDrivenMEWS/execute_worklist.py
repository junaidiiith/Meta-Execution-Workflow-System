from database_funcs import Database
from states import TaskStates


class WorklistExecution:
    def __init__(self):
        self.user = input("Enter your name")
        self.password = input("Enter password")
        self.dbs = Database()
        user = self.find_user()
        while not user:
            self.user = input("Invalid credentials.\nEnter your name")
            self.password = input("Enter your password")
            user = self.find_user()
        self.worklist = [record for record in self.get_worklist()]
        if not self.worklist:
            print("No tasks pending!")
        else:
            self.execute_worklist()
        self.actions = []

    def find_user(self):
        record = {'name':self.user, 'password':self.password}
        return self.dbs.find_one_record('Users', record)['_id']

    def get_worklist(self):
        record = {'name':self.user, 'password':self.password}
        user_id = self.dbs.find_one_record("Users",record)['_id']
        return self.dbs.find_many_records("Worklist", {"user_id":user_id})


    def print_tasks(self):
        worklist = self.worklist
        i = 1
        for w in worklist:
            action_id = w['action']
            action = self.dbs.find_one_record("Actions", action_id)
            self.actions.append(action)
            print(str(i)+')',action['description'])
            i += 1

    def get_task(self, action):
        record = {"action":action['_id']}
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
            return self.dbs.find_one_record("Data",record)
        except:
            print("Record not found for global variable", var)

    def find_in_local(self, var, tid, wid):
        record = {"type":'global','variable':var, "task_id": tid,  "workflow_id":wid}
        try:
            return self.dbs.find_one_record("Data",record)
        except:
            print("Record not found for global variable", var)

    def update_task_state(self, act_or_eve, value):
        wid = act_or_eve['workflow_id']
        name = act_or_eve['task']
        task = self.dbs.find_one_record("Tasks", {"workflow_id": wid, 'name': name})
        temp = task
        task['state'] = value
        self.dbs.update_record("Tasks", temp, task)
        return task

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
                val = self.find_in_global(arg, wid)
                kwargs[arg] = val

            for arg in task.affected_objects['local']:
                t_id = arg[0]
                for var in arg[1]:
                    val = self.find_in_local(var, t_id, wid)
                    kwargs[var] = val

            mod, cls, func = task['handler'].split(',')
            cls = __import__(mod, cls)
            task = self.update_task_state(action, TaskStates.RUNNING.value)
            callback = getattr(cls, func)
            task['data'] = callback(*args, **kwargs)

            self.add_to_local_db(task['data'], task['name'], wid)  # update new local variables defined in the function
            self.add_to_global_db(task['data'], wid)

            task = self.update_task_state(action, TaskStates.FINISHED.value)

            if not len(self.worklist):
                break
            action_no = input("Choose the next action to perform")