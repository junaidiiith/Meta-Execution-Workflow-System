class Specification:
	def __init__(self,uid):
		pass

	def define_workflow(self,name):
		attribs = ['name','owner','task_list','input_para','output_para']
		create_table(name,attribs)

	def define_roles(self):
		attribs = ['name','task_list']
		create_table("roles",attribs)

	def define_tasks(self,)	

