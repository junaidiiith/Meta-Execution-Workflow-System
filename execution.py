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
		task_id = get_attribute_value('Actions',action,'task_id')
		mod,c,f = get_attribute_value('Tasks',task_id,'agent')
		agent = __import__(module)
		i = getattr(agent,c)()
		self.swe, events = getattr(i,f)(self.ew_eid,self.sw_eid,self.swe)
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
		d = {}
		d['Activities'] = ["Description","Type","Task_list","status","input_para","output_para",\
		"finished_list","executing_list"]
		d['Tasks'] = ["activity","owner","status","pre_tasks","post_tasks","input_para","output_para","PSA","Events"]
		d['Events'] = ["activity","Tasks","affected_object","PSA","Events","condition"]
		d['Conditions'] = ["activity","owner","Event"]
		d['Actions'] = ["activity","event_condition","task","object_affected"]


		for key, value in d.items():
			create_table(key,value)


	def create_table(self,table_name,attribs):
		conn = self.conn
		cursor = conn.cursor()
		flag = 0
		if table_name == "Activities":
			flag = 1

		dtypes = {}
		for a in attribs:
			if a == 'id':
				continue
			else:
				dtypes[a] = "varchar(200)"

		s = ""
		for key,value in dtypes.items():
			s += key + " " + value+","

		if flag == 1:
			s += "sw_id int,"
		else:
			s += "sw_id int, ew_id int,"

		q = "create table "+table_name+" (id int not null auto increment," +s+" primary key(id))"
	
		try:
	        print("Creating table "+ table_name, end='')
	        cursor.execute(ddl)
	    except mysql.connector.Error as err:
	        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
	            print("already exists.")
	        else:
	            print(err.msg)
	    else:
	        print("OK")


	def insert_data(self,ew,sw):
		conn = self.conn
		cursor = conn.cursor()

		print "Populating tasks"

		tables = ["Tasks","Events","Conditions","Actions"]
		d = {}
		for w in [ew,sw]:
			x = 0
			for table_name in tables:
				print "Populating "+table_name
				a = json.load(w[table_name])
				s = ""
				k = ""
				for key,value in a.items():
					k += key+","
					s += value+","
				if x == 0:
					k = "ew_id"
					s += ew_id
				else:
					k = "sw_id,ew_id"
					s += sw_id + ","+ ew_id
				q = "insert into "+ table_name +"("+k+") values ("+s+")"
				try:
					cursor.execute(q)
				except:
					print "Some error!!!!!"
				if x == 0:
					t = ""
				else:
					t = "sw_id="+self.sw_id+" and"

				q = "select id from "+table_name+" where "+t+" ew_id="+self.ew_id
				l = []
				for c in cursor:
					l.append(c)
				d[table_name] = l
			x += 1

		print "Populating Activities table"

		k = "Type,Description,Task_List,status,input_para, output_para"
		s = json.load["Activities"]				#edit this part!!!
		q = "insert into Activities ("+k+") values ("+s+")"



	def get_attribute_value(self,table_name,find_key,return_val):
		conn = self.conn
		cursor = conn.cursor()

		query = "select "+return_val+" from "+table_name+\
		" where sw_id="+self.sw_id+" and ew_id="+self.ew_id+ " and id="+find_key
		cursor.execute(q)
		for r in cursor:
			return r
		
	def update_states(self,ew_id,sw_id):
		pass

	def update_task(self,id):
		pass
