from TestApp.mews_signals import *
from uuid import uuid4
from executor.models import *
from specifier.models import *
from django.dispatch import receiver
from executor import utils


@receiver(start_flow, dispatch_uid=uuid4())
def start_workflow(sender, **kwargs):
	'''Create execution workflow instance
	Change state of workflow to started and raise event to start the first task'''
	
	#create WorkflowExec instance
	try:
		meta_exec = kwargs['MetaExec']
		Userflow = Workflow.objects.get(id=meta_exec.data['UserFlow'])
		assert Userflow is not None
		flow  = Userflow
		workflow_exec = utils.get_workflow_exec(Userflow)
		meta_exec.data['UserExec'] = workflow_exec.id
		utils.save_event(1,workflow_exec.id,2)
		meta_exec.save()
		MetaUserAssoc(user=workflow_exec, meta=meta_exec).save()
	except:
		flow = kwargs['MetaFlow']
		workflow_exec = utils.get_workflow_exec(flow)
		utils.save_event(1,workflow_exec.id,3)
		workflow_exec.data['UserFlow'] = kwargs['UserFlow'].id
		workflow_exec.save()

	#create TaskExec instance of start task
	task = Task.objects.get(workflow=flow.id, name='start')
	init_task_exec = utils.get_task_exec(task,workflow_exec)

	#Add event of start task of 'flow' finished.
	print("-----Created workflow objects and workflow started-----")
	#find task with name '_start_' of workflow with id = flow.id
	#Find the next tasks of start task completed event
	event = utils.save_event(2,init_task_exec.id,5)
	print("Start task ended event")
	if flow.workflow_type == 1:
		print("Find next tasks")
		utils.add_output_tasks(event)
	else:
		print("Saving event: ", event.id, " for User workflow ", workflow_exec.workflow.name)
		workflow_exec.data['event_raised'] = event.id
		workflow_exec.save()

@receiver(end_flow, dispatch_uid=uuid4())
def end_workflow(sender, **kwargs):
	flow_exec = kwargs['flow_exec']
	utils.save_event(1,flow_exec.id,5)
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
	flow_exec = task_exec.workflow_exec
	if flow_exec.state != 3:
		utils.save_event(1,flow_exec.id,3)

	event = utils.save_event(2,task_exec.id,2)

	#update state of task as started
	execute_task.send(sender, task_exec=task_exec)
	# print("-----Workflow task-----", task_exec.task.name, " finished")


@receiver(end_task, dispatch_uid=uuid4())
def end_workflow_task(sender, **kwargs):
	task_exec = kwargs['task_exec']
	print("ending task", task_exec.task.name)
	flow_exec = task_exec.workflow_exec
	event = utils.save_event(2,task_exec.id,5)
	print("-----Task execution ended for ", task_exec.task.name, " -----")
	if flow_exec.workflow.workflow_type == 1:
		utils.add_output_tasks(event)
	else:
		flow_exec.data['event_raised'] = event.id
		flow_exec.save()

@receiver(execute_task, dispatch_uid=uuid4())
def execute_workflow_task(sender, **kwargs):
	'''Parse the handler and execute the task''' 
	task_exec = kwargs['task_exec']
	if task_exec.task.task_type == 1:
		utils.dispatch(task_exec)
		utils.update_current_tasks_list(task_exec.workflow_exec)
	print("-----Executed workflow task: ", task_exec.task.name, " -----")
	end_task.send(sender, task_exec=task_exec)

@receiver(stop_task, dispatch_uid=uuid4())
def stop_workflow_task(sender, **kwargs):
	task_exec = kwargs['task_exec']
	print("-----Workflow stopped-----")
