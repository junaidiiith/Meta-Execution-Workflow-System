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
	else:
		obj = TaskExec.objects.get(pk=object_id)
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

def event_expression_check(expr):
	True

def evaluate_conditions(conditions):
	return True

def possible(task):
	if event_expression_check(task.event_expression) and evaluate_conditions(task.conditions):
		return True
	return False


def find_next_tasks(event):
	#find the possible next tasks
	#Check for every task if all the preconditions and events have occured for the tasks to be added to the execution queue
	tasks = event.tasks  #list of ids of all the possible next tasks
	possible_tasks = list()
	for task in tasks:
		if possible(task):
			possible_tasks.append(task)

	return possible_tasks


def add_tasks_to_unassigned_list(tasks, workflow_exec):
	for task in tasks:
		if task.role == 'system':
			task_exec = get_task_exec(task, workflow_exec)
			save_event(2,task_exec.id,1)
		else:
			start_task.send(sender,task,workflow_exec)

def add_output_tasks(event):
	tasks = find_next_tasks(event)
	
	assert tasks is not None
	if len(task) == 1 and task.name == 'end':
		end_workflow.send(task.workflow)
	for task in tasks:
		add_tasks_to_unassigned_list(task, workflow_exec)