from event_handler import EventHandler

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

Eh = EventHandler()
Uh = EventHandler()

Eh.add_event(mw['t1'])
Uh.add_event(uw['u1'])

me=Eh.actions.keys()
while len(me):
	for eve in me:
		Eh.register_action(eve)
		Eh.fire(eve,Uh,uh=Uh)

	me = Eh.actions.keys()
