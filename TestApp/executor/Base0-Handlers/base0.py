from executor.models import *
from specifier.models import *
from executor.event_handlers import *
from executor.utils import *
from TestApp import mews_signals


def create_workflow_instance(**kwargs):
	task_exec = kwargs['task_exec']
	workflow_exec = task_exec.workflow_exec
	flowId = workflow_exec.data['Userflow']
	flow = Workflow.objects.get(id=flowId)
	assert flow is not None
	start_workflow.send(sender=None, Userflow=None, MetaExec=workflow_exec)
	
def update_workflow_state(**kwargs):
	task_exec = kwargs['task_exec']
	workflow_exec = task_exec.workflow_exec
	flowId = workflow_exec.data['UserExec']
	flow = WorkflowExec.objects.get(id=flowId)
	assert flow is not None
	save_event(1, flow.id, 3)

def get_a_task(**kwargs):
	task_exec = kwargs['task_exec']
	workflow_exec = task_exec.workflow_exec
	flowId = workflow_exec.data['UserExec']
	flow = WorkflowExec.objects.get(id=flowId)
	assert flow is not None

	event = Eventdb.objects.get(id=flow['raised_event'])
	assert event in not None

	tasks, workflow_exec = find_next_tasks(event)

	assert tasks is not None
	user_tasks = []
	for task in tasks:
		user_task_exec = get_task_exec(task, workflow_exec)
		event = save_event(2,user_task_exec.id,1)
		user_tasks.append(user_task_exec.id)

	task_exec.data['user_tasks'] = user_tasks



def check_resources(**kwargs):
	print("resources available")

def execute(**kwargs):
	task_exec = kwargs['task_exec']
	workflow_exec = task_exec.workflow_exec
	flowId = workflow_exec.data['UserExec']
	flow = WorkflowExec.objects.get(id=flowId)
	assert flow is not None
	print("Execution complete")
	# dispatch()

def end(**kwargs):
	pass
