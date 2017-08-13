mw = {
    "t1":{"name":"get a task","type":"meta","handler": "MEWS.tasks.Tasks.get_a_task","condition":None,"output_tasks":"t2"},
    "t2":{"name":"Check task","type":"meta","handler":"MEWS.tasks.Tasks.check_task","condition":True,"output_tasks":("t3,t4")},
    "t3":{"name":"Execute","type":"meta","handler":"MEWS.tasks.Tasks.execute","condition":None,"output_tasks":"t1"},
    "t4":{"name":"End","type":"meta","handler":"MEWS.tasks.Tasks.end","condition":None,"output_tasks":None}
}

uw = {
    "u1":{"name":"Create account","type":"user","handler":"UW.tasks.Tasks.create_account","condition":None,"output_tasks":"u2"},
    "u2":{"name":"Check CGPA","type":"user","handler":"UW.tasks.Tasks.check_cg","condition":"Cgpa >= 7","output_tasks":"u3,u4"},
    "u3":{"name":"Call Interview","type":"user","handler":"UW.tasks.Tasks.call_interview","condition":None,"output_tasks":None},
    "u4":{"name":"reject","type":"user","handler":"UW.tasks.Tasks.reject","condition":None,"output_tasks":None},
}

from action_handler import ActionHandler
class EventHandler:
	def __init__(self):
		self.actions = {}
		# self.actions[event] = value
		self.actionhandler = ActionHandler()

	def register_action(self,event,callback=None):
        	if callback is None:
            		callback = getattr(self.actionhandler,'execute')
        	self.actions[str(event)] = {"execute":callback}

    	def add_event(self,event):
    		self.actions[str(event)] = {}

    	def fire(self,event,*args,**kwargs):
    		# print(self.actions)
		for action,value in self.actions[event].items():
			print("Executing ",event)
			value(event,*args,**kwargs)
		self.actions = {}
		
		for event in self.actionhandler.output_events:
			self.add_event(event)


