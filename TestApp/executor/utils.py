from TestApp.mews_signals import *
from executor.models import *
from specifier.models import *
from django.dispatch import receiver
from executor.utils import *


def dispatch(task_exec):
	print("Task ",task_exec.task.name," executed successfully")

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
	return task_exec

def check_rule_expression(expr):
	print(expr)
	if expr:
		gate = expr['gate']
		if gate.lower() == 'and':
			# print("Checking here")
			return all([evaluate_rule(rule_id) for rule_id in expr['rules']])
		else:
			return any([evaluate_rule(rule_id) for rule_id in expr['rules']])
	return True

def evaluate_rule(rule_id):
	rule = Rule.objects.get(id=rule_id)
	# print("evaluate_rule: ", rule.condition)
	f = int(input())
	if f == 1:
		return True
	return False
	return check_event(rule.event) and check_condition(rule.condition)

def check_condition(condition):
	return True

def check_event(event):
	return True


def possible(task):
	if check_rule_expression(task.rule_expression):
		return True
	return False

def get_event(eventdb):
	if eventdb.object_type == 1:
		pass
	else:
		task_exec = TaskExec.objects.get(id = eventdb.object_id)
		event = Event.objects.get(task=task_exec.task, state=eventdb.state )
		return event, task_exec.workflow_exec
def get_event_db(event):
	Eventdb.objects.get()


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
			if possible(task):
				possible_tasks.append(task)

	return possible_tasks, workflow_exec


def add_task_to_unassigned_list(task, workflow_exec):
	task_exec = get_task_exec(task, workflow_exec)
	event = save_event(2,task_exec.id,1)
	# print(task.role)
	if task.role.name == 'system':
		# print("Starting task: ", task.name)
		start_task.send(None,task_exec=task_exec ,flow_exec=workflow_exec)

def add_output_tasks(eventdb):
	tasks, workflow_exec = find_next_tasks(eventdb)
	# print("tasks: ", tasks)
	assert tasks is not None
	if len(tasks) == 1 and tasks[0].name.lower() == 'end':
		end_flow.send(None, flow_exec=workflow_exec)
	else:
		for task in tasks:
			add_task_to_unassigned_list(task, workflow_exec)