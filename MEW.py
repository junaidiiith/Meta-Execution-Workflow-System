from MSW import MSW

class MEW(object):
	"""docstring for MEW"""
	def __init__(self):
		self.tasks = ["Basic workflow definition","Define Atomic tasks","Define roles","Define Sequence", "Link roles and tasks"]
		self.workflow = None

	def create_workflow_instance(self):
		self.workflow = MSW()

	def Update_state_running(self):
		self.workflow.state = "Running"

	def execute_task(self,task):
		if task == self.tasks[0]:
			self.workflow.basic_workflow_definition()
		elif task == self.tasks[1]:
			self.workflow.define_atomic_tasks()
		elif task == self.tasks[2]:
			self.workflow.define_roles()
		elif task == self.tasks[3]:
			self.workflow.sequence_of_tasks(self.workflow.tasks)
			self.workflow.conditions_on_tasks(self.workflow.sequence)
		elif task == self.tasks[4]:
			self.workflow.link_roles_to_tasks(self.workflow.tasks, self.workflow.roles)

	def check_resources(self,task):
		return True

	def check_availablity(self,a):
		if a < len(self.tasks):
			return True
		return False

	def get_task(self,i):
		return self.tasks[i]

	def update_state_complete(self):
		self.workflow.state = "Complete"

	def run(self):
		i = 0
		self.create_workflow_instance()
		self.Update_state_running()
		while True:
			if not self.check_availablity(i):
				break
			task = self.get_task(i)
			if not self.check_resources(task):
				continue
			self.execute_task(task)
			i = i + 1
		self.update_state_complete()
		self.workflow.run()

if __name__ == "__main__":
	m = MEW()
	m.run()
		