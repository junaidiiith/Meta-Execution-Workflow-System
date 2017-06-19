class SpecifyWorkflow:
    def __init__(self,**kwargs):
        self.sw = kwargs.get('sw')
        self.specify_worklow()

    def specify_worklow(self):
        print "Start defining tasks"

        task_specs = {}
        task_vals = {}
        name = raw_input("Enter the name of the task")
        while  name != "End":
            cls = raw_input("Enter the class of the task")
            if cls == "ExclusiveChoice":
                pass
            if cls == "Join":
                pass
            if cls == "Split":
                pass

            if cls == "Cancel":
                pass

            man = raw_input("Enter if task is manual or automated")
            output_tasks = raw_input("Enter output task names")
            input_tasks = raw_input("Enter the input tasks")
            owner = raw_input("Enter the type of owner")
            agent = raw_input("Enter the library that will execute the task")
            description = raw_input("Enter the description of the task")
            type = 'user'
            output_tasks = output_tasks.split()
            input_tasks = input_tasks.split()
            task_vals['name'] = name
            task_vals['owner'] = owner
            task_vals['agent'] = agent
            task_vals['description'] = description
            task_vals['type'] = type
            task_vals['output_tasks'] = output_tasks
            task_vals['input_tasks'] = input_tasks
            task_specs['name'] = task_vals
            name = raw_input("Enter the name of the task")
            task_vals = {}