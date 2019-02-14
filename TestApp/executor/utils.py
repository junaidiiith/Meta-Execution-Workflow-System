from TestApp.mews_signals import *
from executor.models import *
from specifier.models import *
import ast
from executor.Base_Handlers import base0


def my_import(name):
        __import__(name.rsplit('.', 1)[0])
        components = name.split('.')
        mod = __import__(components[0])
        print(mod)
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

def dispatch(task_exec, *args, **kwargs):
	handler = task_exec.task.handler
	cls, func = my_import("executor.Base_Handlers.base0"), handler['function']
	callback = getattr(cls, func)
	kwargs['task_exec'] = task_exec
	d = callback(*args, **kwargs) or None
	print("Task ", task_exec.task.name, " executed successfully")
	return d


def save_event(object_type, object_id, state):
	event = EventDB(object_type=object_type, object_id=object_id, state=state)
	event.save()

	if object_type == 1:
		obj = WorkflowExec.objects.get(pk=object_id)
		print("Event saved: ", obj.workflow.name," "+str(event.state))
	else:
		obj = TaskExec.objects.get(pk=object_id)
		print("Event saved: ", obj.task.name," "+str(event.state))
	obj.state = state
	obj.save()
	return event

def get_workflow_exec(flow):
	assert flow is not None
	workflow_exec = WorkflowExec(workflow=flow, state=1, data={})
	workflow_exec.save()
	return workflow_exec

def get_start_task(flow):
	assert flow is not None
	task = Task.objects.filter(workflow=flow.id, name='start')
	assert task is not None and len(task) == 1
	task_exec = TaskExec(workflow_exec=flow, task=task, state=1)
	task_exec.save()
	return task_exec

def get_task_exec(task,flow_exec):
	assert task is not None
	task_exec = TaskExec(workflow_exec=flow_exec, task=task, state=1)
	task_exec.save()
	print("Task :", task, " and flow: ", flow_exec)
	return task_exec

def check_rule_expression(expr, workflow_exec):
	if expr:
		gate = expr['gate']
		if gate.lower() == 'and':
			# print("Checking here")
			return all([evaluate_rule(rule_id, workflow_exec) for rule_id in expr['rules']])
		else:
			return any([evaluate_rule(rule_id, workflow_exec) for rule_id in expr['rules']])
	return True

def evaluate_rule(rule_id, workflow_exec):
	rule = Rule.objects.get(id=rule_id)
	print("evaluate_rule: ", rule.condition, rule.event)
	return check_event(rule.event, workflow_exec) and check_condition(rule.condition, workflow_exec)

def check_condition(condition, workflow_exec):
	# return True
	print(workflow_exec.workflow.constants)
	if condition is None:
		return True
	print("Workflow data",workflow_exec.data)
	workflow_exec.data['CGPA'] = '9'
	# constant = workflow_exec.workflow.constants[condition.constant]
	constant = str(condition.constant)
	operand = str(workflow_exec.data[condition.operand])
	operator = condition.operator
	print(operand,operator,constant)
	expr = eval(operand+operator+constant)
	return expr

def check_event(event, workflow_exec):
	try:
		for t in TaskExec.objects.filter(workflow_exec=workflow_exec):
			print(t.task.name,t.task.id)
		print("Event task is: ", event.task.name, " id: ", event.task.id)
		taskexec = TaskExec.objects.filter(workflow_exec=workflow_exec).filter(task=Task.objects.get(id=event.task_id))[0]
		eventdb = EventDB.objects.filter(object_type=2, object_id=taskexec.id, state=event.state)
		return len(eventdb) > 0
	except:
		return False

def possible(task, workflow_exec):
	if check_rule_expression(task.rule_expression, workflow_exec):
		return True
	return False

def get_event(eventdb):
	if eventdb.object_type == 1:
		pass
	else:
		task_exec = TaskExec.objects.get(id = eventdb.object_id)
		event = Event.objects.get(task=task_exec.task, state=eventdb.state )
		print("Task is: ", task_exec.task.name ," and workflow exec is: ", task_exec.workflow_exec)
		return event, task_exec.workflow_exec


def update_current_tasks_list(workflow_exec):
	try:
		current_tasks = workflow_exec.data['current_user_tasks']
		newList = list()
		for task in current_tasks:
			print("Checking completion of ", TaskExec.objects.get(id=task).task.name)
			if TaskExec.objects.get(id=task).state not in [5,6]:
				print("Adding ", TaskExec.objects.get(id=task).task.name, " to new list of current_user_tasks")
				newList.append(task)
		workflow_exec.data['current_user_tasks'] = newList
		if not newList:
			workflow_exec.data['task_availibility'] = False
		print("current_user_tasks are ", newList)
	except:
		pass

def find_next_tasks(eventdb):
	#find the possible next tasks
	#Check for every task if all the preconditions and events have occured for the tasks to be added to the execution queue
	event, workflow_exec = get_event(eventdb)
	rules = Rule.objects.filter(event=event)
	possible_tasks = list()
	for rule in rules:
		task_rules = Task_Rule.objects.filter(rule=rule)
		for task_rule in task_rules:
			task = task_rule.task
			print("checking possible: ", task.name)
			if possible(task, workflow_exec):
				possible_tasks.append(task)
				print("Task: ", task.name, " possible")
	# print("Next task are: ", end="")
	# for task in possible_tasks:
	# 	print(task.name)
	return possible_tasks, workflow_exec


def add_task_to_unassigned_list(task, workflow_exec):
	try:
		current_user_tasks = workflow_exec.data['current_user_tasks']
		if not current_user_tasks:
			task_exec = get_task_exec(task, workflow_exec)
			print("Starting execution of ", task.name)
			start_task.send(None, task_exec=task_exec)
		# print("Current tasks ", current_user_tasks)
		else:
			for user_task in current_user_tasks:

				task_exec = get_task_exec(task, workflow_exec)
				task_exec.data['user_task'] = user_task	
				task_exec.save()
				event = save_event(2,task_exec.id,1)

				if task.role.name == "system" or TaskExec.objects.get(id=user_task).task.role.name == "system":
					print("Starting task ", task_exec.task.name)
					start_task.send(None, task_exec=task_exec)
	except:
		task_exec = get_task_exec(task, workflow_exec)
		save_event(2,task_exec.id,1)
		# print(task.role)
		if task.role.name == 'system':
			print("Starting task: ", task.name)
			start_task.send(None,task_exec=task_exec)

def add_output_tasks(eventdb):
	tasks, workflow_exec = find_next_tasks(eventdb)
	# print("tasks: ", tasks)
	assert tasks is not None
	if len(tasks) == 1 and tasks[0].name.lower() == 'end':
		end_flow.send(None, flow_exec=workflow_exec)
	else:
		for task in tasks:
			add_task_to_unassigned_list(task, workflow_exec)

