mw = {
	"t1":{"name":"get a task","handler": "MEWS.tasks.Tasks.get_a_task","condition":None,"output_tasks":"t2"},
	"t2":{"name":"Check task","handler":"MEWS.tasks.Tasks.check_task","condition":True,"output_tasks":("t3,t4")},
	"t3":{"name":"Execute","handler":"MEWS.tasks.Tasks.execute","condition":None,"output_tasks":"t1"},
	"t4":{"name":"End","handler":"MEWS.tasks.Tasks.end","condition":None,"output_tasks":None}
}

uw = {
	"u1":{"name":"Create account","handler":"UW.tasks.Tasks.create_account","condition":None,"output_tasks":"u2"},
	"u2":{"name":"Check CGPA","handler":"UW.tasks.Tasks.check_cg","condition":"Cgpa >= 7","output_tasks":("u3","u4")},
	"u3":{"name":"Call Interview","handler":"UW.tasks.Tasks.call_interview","condition":None,"output_tasks":None},
	"u4":{"name":"reject","handler":"UW.tasks.Tasks.reject","condition":None,"output_tasks":None},
}
class Tasks:
	def get_a_task(self,uwhandler,*args,**kwargs):
		assert uwhandler is not None
		print("In get a task!! What's up")
		return uwhandler.actions.keys()

	def check_task(self,uwhandler):
		return uwhandler or uwhandler.actions.keys

	def execute(self,uwhandler):
		# tsk = uwhandler

		# t = uw['u1']
		# uwhandler.add_event(t)
		
		ue = uwhandler.actions.keys()
		# print(type(ue))
       		while len(ue):
            		for eve in ue:
                		uwhandler.register_action(eve)
                		uwhandler.fire(eve)
            		ue = uwhandler.actions.keys()
