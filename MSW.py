class MSW(object):
	"""docstring for ClassName"""
	def __init__(self):
		self.roles = []
		self.tasks = []
		self.sequence = []
		self.conditions = {}
		self.linked_roles = {}
		self.state = "Ready"

	def define_roles(self):
		roles = []
		print "Enter roles for "+ self.basic_workflow_definition
		while True:
			print "Enter your choice"
			print "1: Enter a role"
			print "2: Done entering roles"
			c = input()
			if c == 1:
				roles.append(raw_input())
			elif c == 2:
				break
			else:
				print "Wrong input"
		self.roles = roles

	def basic_workflow_definition(self):
		print "Enter the description of workflow"
		self.basic_workflow_definition = raw_input()

	def define_atomic_tasks(self):
		print "Define atomic tasks"
		print "Enter your tasks"
		tasks = []
		while True:
			print "Enter your choice"
			print "1) Task name"
			print "2) Quit entering tasks"
			c = input()
			if c == 1:
				tasks.append(raw_input())
			elif c == 2:
				break
			else:
				print "Wrong input"
		self.tasks = tasks

	def sequence_of_tasks(self,tasks):
		print "Tasks are:"
		for task in tasks:
			print str(tasks.index(task)) + ")" + str(task)

		sequence = []
		print "Enter the sequence"
		print "Enter the transition A to B. For example 1 4 implies transition from 1 to 4"
		print "press -1 to stop entering sequences"
		while True:
			transition = raw_input()
			transition = transition.strip().split()
			if transition[0] == "-1":
				break
			if len(transition) != 2:
				print "Wrong transition"
			else:
				a = transition[0]
				b = transition[1]
				sequence.append((tasks[int(a)],tasks[int(b)]))
		self.sequence = sequence


	def conditions_on_tasks(self,sequence):
		print "transitions in a sequence are:"
		for transition in sequence:
			print transition[0] + "---->" + transition[1]
		conditions = {}
		print "Enter conditions on transitions"
		for transition in sequence:
			print "Enter condition on transition from " + transition[0] + " to "+ transition[1]
			condition = raw_input()
			conditions[transition] = condition
		self.conditions = conditions

	def link_roles_to_tasks(self,tasks, roles):
		print "Tasks are:"
		for task in tasks:
			print str(tasks.index(task)) + ")" + str(task)

		for role in roles:
			print str(roles.index(role)) + ")" + str(role)


		linked_roles = {}
		print "1 2 3 ==> Role x is a part of tasks 1,2,3"
		for role in roles:
			print "Enter task numbers from above for role :"+ str(role)
			linked_tasks = raw_input().strip().split()
			linked_roles[role] = linked_tasks
		self.linked_roles = linked_roles

	def run(self):
		print "These are the tasks that can be executed"
		for task in self.tasks:
			print str(self.tasks.index(task)) + ")" + str(task)

