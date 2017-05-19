import json
import mysql.connector
from collections import namedtuple



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
		self.swe = getattr(i,f)(self.sw_eid,self.swe)
		return update_states(ew_id,action)


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
		conn = self.conn
		cursor = conn.cursor()
		
		q = []

		q1 = "Create table Conditions (cid int not null auto increment, description varchar(400), primary key(cid))"

		q2 = "create table Events (eid int not null auto increment, conditions varchar(400), aid int null, affected_object varchar(400),primary key(eid))"

		q3 = "create table Actions (aid int not null auto increment, eid int, primary key(aid))"

		q4 = "create table Tasks (tid int not null auto increment, wid int, status varchar(100),IP varchar(200),OP varchar(200), IE varchar(400),OE varchar(400), agent varchar(500), PreT varchar(300), PosT varchar(300), primary key(tid)"


		q5 = "create table E_Activities (ew_id int not null auto increment, sw_id int, description varchar(300),task_list varchar(500), status varchar(100),executing_tasks varchar(50),finished_tasks varchar(400), primary key(ew_id))"

		q6 = "create table S_Activities (sw_id int not null auto increment, task_list varchar(500),status varchar(400),executing_tasks varchar(50), finished_tasks varchar(400), primary key(sw_id))"


		q = [q1,q2,q3,q4,q5,q6]
		for query in q:
			try:
		        print("Creating tables "+ table_name, end='')
		        cursor.execute(query)
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

		tables = ["Tasks","Events","Conditions","Actions"]
		d={}
		for table_name in tables:
			a=json.load(w[table_name])
			k=""
			s=""
			for key, value in a.items():
					k += key+","
					s += value+","
					q = "insert into "+ table_name +"("+k+") values ("+s+")"
					try:
						cursor.execute(q)
					except:
						print "ERROR!!! CAN NOT INSERT DATA"





	def get_attribute_value(self,table_name,find_key,return_val):
		conn = self.conn
		cursor = conn.cursor()

		query = "select "+return_val+" from "+table_name+\
		" where sw_id="+self.sw_id+" and ew_id="+self.ew_id+ " and id="+find_key
		cursor.execute(q)
		for r in cursor:
			return r
		
	def update_states(self,ew_id,tid):
		cursor = self.conn.cursor()

