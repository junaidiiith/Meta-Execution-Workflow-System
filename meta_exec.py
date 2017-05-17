import json

class MEW:
	def __init__(self):
		self.state = "start"
		self.id = 10 #some random id

	def create_workflow_instance(self,w):
		self.wfinstance = (self.id,w.id)

	def update_state_running(self):
		self.state = "running"

	def get_a_task(self,w):
		