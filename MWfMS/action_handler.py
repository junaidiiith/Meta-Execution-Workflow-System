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
import ast

from my_import import imp
class ActionHandler:
    def __init__(self):
	self.events = {}
    	self.output_events = []

    def execute(self,action,*args,**kwargs):
        print(type(action))
    	action = ast.literal_eval(action)
    	assert action is not None
        # print(action['handler'])
        print(type(action))
    	x = action['handler'].rsplit('.',1)
        # print(x)
        # print(type(x))
        cl,fc = imp(x[0])(),x[1]
        # print(cl)
    	callback = getattr(cl,fc)

    	action["output"]= callback(*args,**kwargs)

    	if action['condition']:
    		output_tasks = action['output_tasks'][0]
    	else:
    		output_tasks = action['output_tasks'][1]

    	self.output_events = output_tasks

