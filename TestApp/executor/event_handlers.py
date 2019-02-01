from TestApp.mews_signals import *
from uuid import uuid4
from executor.models import *
from specifier.models import *
from django.dispatch import receiver
from executor.utils import *



@receiver(start_flow, dispatch_uid=uuid4())
def start_workflow(sender, **kwargs):
	'''Create execution workflow instance
	Change state of workflow to started and raise event to start the first task'''
	flow = kwargs['flow']
	#create WorkflowExec instance
	workflow_exec = get_workflow_exec(flow)
	save_event(1,workflow_exec.id,2)
	#create TaskExec instance of start task
	task = Task.objects.get(workflow=flow.id, name='start')
	init_task_exec = get_task_exec(task,workflow_exec)

	#Add event of start task of 'flow' finished.
	print("-----Created workflow objects and workflow started-----")
	#find task with name '_start_' of workflow with id = flow.id
	#Find the next tasks of start task completed event
	event = save_event(2,init_task_exec.id,5)
	print("Start task ended event")
	add_output_tasks(event)

@receiver(end_flow, dispatch_uid=uuid4())
def end_workflow(sender, **kwargs):
	flow_exec = kwargs['flow_exec']
	save_event(1,flow_exec.id,5)
	'''Update the states and remove the instance of user workflow from the active instances'''
	print("-----Workflow Ended-----")


@receiver(stop_flow, dispatch_uid=uuid4())
def stop_workflow(sender, **kwargs):
	flow_exec = kwargs['flow_exec']
	'''Update the state of the workflow as exception occured'''
	print("-----Workflow Stopped-----")


@receiver(start_task, dispatch_uid=uuid4())
def start_workflow_task(sender, **kwargs):
	'''check if task is meta or user and proceed accordingly'''
	task_exec = kwargs['task_exec']
	flow_exec = kwargs['flow_exec']
	event = save_event(2,task_exec.id,2)

	#update state of task as started
	execute_task.send(sender, task_exec=task_exec, flow_exec=flow_exec)
	# print("-----Workflow task-----", task_exec.task.name, " finished")


@receiver(end_task, dispatch_uid=uuid4())
def end_workflow_task(sender, **kwargs):
	task_exec = kwargs['task_exec']
	flow_exec = kwargs['flow_exec']
	event = save_event(2,task_exec.id,5)
	print("-----Task execution ended for ", task_exec.task.name, " -----")
	add_output_tasks(event)

@receiver(execute_task, dispatch_uid=uuid4())
def execute_workflow_task(sender, **kwargs):
	'''Parse the handler and execute the task''' 
	task_exec = kwargs['task_exec']
	flow_exec = kwargs['flow_exec']
	dispatch(task_exec)
	print("-----Executed workflow task: " , task_exec.task.name," -----")
	end_task.send(sender=None, task_exec=task_exec, flow_exec=flow_exec)

@receiver(stop_task, dispatch_uid=uuid4())
def stop_workflow_task(sender, **kwargs):
	task_exec = kwargs['task_exec']
	flow_exec = kwargs['flow_exec']
	print("-----Workflow stopped-----")

