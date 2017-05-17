import json
import mysql.connector


class Execute:
	def __init__(self,ew,sw):

		create_templates(ew,sw)
		self.ew_eid,self.sw_eid = insert_data(ew,sw)
		self.swe = None
		self.data = None
		self.output_json = "myapplication.json"
		self.conn = create_db_connection()
	
	def create_db_connection(self):
		config = {
		  'user': 'root',
		  'password': '123',
		  'host': '127.0.0.1',
		  'database': 'base-0',
		  'raise_on_warnings': True,
		}
		return mysql.connector.connect(**config)


	def execute_ew(self):

		events = initialize()
		actions = get_actions(events)
		while len(actions):
			events = execute_ew_task(actions)
			actions = get_actions(events)

	def execute_ew_task(self,actions):
		events = []
		for action in actions:
			events.append(execute(action))
		return events

	def execute(self,action):
		fname = get_function_name(action)
		agent = __import__(ew[fname][agent])
		i = getattr(agent,agent)()
		self.swe, events = getattr(i,fname)(self.ew_eid,self.sw_eid,self.swe)
		update_task(action)
		update_states(ew_id,sw_id)
		return events

	def initialize(self):
		tasks = ew['tasks']
		start = tasks['start']
		return execute(start,self.ew.agents)


	def get_actions(self,events):
		condition_actions = get_conditions(events)
		actions = []
		for pair in condition_actions:
			if check_condition(pair[0]):
				actions.append(pair[1])

		return actions

	def get_conditions(self,events):
		rules = self.ew[eca_rules]
		condition_actions = []
		for event in events:
			try:
				condition_actions.append(rules[event])
			except:
				print "No such action present ", event


	def check_condition(self,condition):
		event = self.ew['conditions'][condition]['event']
		val = get_value_from_task_template(event['task'],event['task_var'])
		s = str(val) + condition[len(task_var)-1:]
		if eval(s):
			return True
		return False

	def create_templates(self):
		table_name = "Activities"
		attribs = ["type","Task_list","status","input_para","output_para","finished_list","executing_list"]
		create_table(table_name,attribs)
		
		table_name = "Tasks"
		attribs = ["activity","owner","status","pre_tasks","post_tasks","input_para","output_para","PSA","Events"]
		create_table(table_name,attribs)

		table_name = "Events"
		attribs = ["activity","Tasks","affected_object","PSA","Events","condition"]
		create_table(table_name,attribs)

		table_name = "Conditions"
		attribs = ["activity","owner","Event"]
		create_table(table_name,attribs)

		table_name = "Actions"
		attribs = ["activity","event_condition","task","object_affected"]
		create_table(table_name,attribs)



	def create_table(self,table_name,attribs):
		conn = self.conn
		cursor = conn.cursor()

		s = "Create table "+table_name+" ('id int not null auto increment','desc varchar(400)',\
		'Task_List varchar(500)',"

	def insert_data(self,ew,sw):
		conn = self.conn
		cursor = conn.cursor()

	def update_states(self,ew_id,sw_id):
		pass

	def update_task(self,id):
		pass

	def get_function_name(self,action):
		pass
