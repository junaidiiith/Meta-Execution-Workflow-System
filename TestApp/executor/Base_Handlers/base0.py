from executor.models import *
from specifier.models import *
from executor.event_handlers import *
from executor import utils
from TestApp import mews_signals


def create_workflow_instance(**kwargs):
	task_exec = kwargs['task_exec']
	workflow_exec = task_exec.workflow_exec

	start_flow.send(sender=None, Userflow=None, MetaExec=workflow_exec)
	
def update_workflow_state(**kwargs):
	task_exec = kwargs['task_exec']
	workflow_exec = task_exec.workflow_exec
	print(workflow_exec.data)
	flowId = workflow_exec.data['UserExec']
	flow = WorkflowExec.objects.get(id=flowId)
	assert flow is not None
	utils.save_event(1, flow.id, 3)

def get_a_task(**kwargs):
	task_exec = kwargs['task_exec']
	workflow_exec = task_exec.workflow_exec
	flowId = workflow_exec.data['UserExec']
	flow = WorkflowExec.objects.get(id=flowId)
	assert flow is not None
	print(flow.workflow.name, flow.data)
	event = EventDB.objects.get(id=flow.data['event_raised'])
	
	assert event is not None

	tasks, _ = utils.find_next_tasks(event)

	assert tasks is not None
	if len(tasks) == 1 and tasks[0].name.lower() == 'end':
		workflow_exec.data['current_user_tasks'] = {}
		workflow_exec.data['task_availibility'] = False
		workflow_exec.save()
	else:
		user_tasks = []
		for task in tasks:
			user_task_exec = utils.get_task_exec(task, flow)
			event = utils.save_event(2,user_task_exec.id,1)
			user_tasks.append(user_task_exec.id)
		print("Adding user tasks for execution: ", user_tasks)
		try:
			workflow_exec.data['current_user_tasks'] += user_tasks
		except:
			workflow_exec.data['current_user_tasks'] = user_tasks
		workflow_exec.data['task_availibility'] = True
		workflow_exec.save()

def check_resources(**kwargs):
	print("resources available")

def execute(**kwargs):
	task_exec = kwargs['task_exec']
	print("Executing ", task_exec.task.name, task_exec.data)
	user_task = task_exec.data['user_task']
	assert user_task is not None
	workflow_exec = task_exec.workflow_exec

	UserflowId = task_exec.workflow_exec.data['UserExec']
	Userflow = WorkflowExec.objects.get(id=UserflowId)

	execute_task.send(None, task_exec=TaskExec.objects.get(id=user_task))
	assert Userflow is not None
	
	workflow_exec.data['current_user_tasks'].remove(user_task)
	utils.update_current_tasks_list(workflow_exec)
	workflow_exec.save()
	
	# dispatch()   #Code to execute the task, some processing

def end(**kwargs):
	pass
