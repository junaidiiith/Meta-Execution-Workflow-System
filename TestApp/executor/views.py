from django.shortcuts import render, get_object_or_404, redirect
from specifier.models import *
from executor.models import *
from executor.forms import CustomForm
from TestApp.mews_signals import *
import executor.event_handlers
from django.forms import formset_factory
from django import forms
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from executor.forms import RoleAssignmentForm
from specifier.utils import *
from django.template.defaulttags import register
# Create your views here.

PENDING = 'Pending'
READY = 'Ready' #ready is assigned
RUNNING = 'Running'
STOPPED = 'Stopped'
ENDED = 'Ended'
EXCEPTION_OCCURED = 'Exception occured'

states = {1: PENDING, 2: READY, 3: RUNNING, 4: STOPPED, 5: ENDED, 6: EXCEPTION_OCCURED}



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def get_start_task(workflow):
	task = Task.objects.filter(workflow=workflow.id, name='start')
	assert task is not None
	return task

def get_tasks(tasks):
	nxttasks = ""
	for tsk in tasks:
		nxttasks += TaskExec.objects.get(id=tsk).task.name + " "
	return nxttasks

def home(request):
	#To Do, Only show the running workflows based on logged in users role
	allWfs = WorkflowExec.objects.all().exclude(state=5).exclude(state=6)    #Add current task attr before rendering
	allWfs = [w for w in allWfs if w.workflow.workflow_type == 1]

	running = list()
	for workflow_exec in allWfs:
		print(workflow_exec.data)
		workflow_exec.current_tasks = get_tasks(workflow_exec.data['current_user_tasks'])
		workflow_exec.ufo = WorkflowExec.objects.get(id=workflow_exec.data['UserExec'])
		running.append(workflow_exec)

	ready = Workflow.objects.filter(workflow_type=2)
	return render(request, 'home.html', {'running': running, 'user': request.user, 'ready': ready, 'states': states})

def get_meta_workflows():
	choices = list()
	workflows = Workflow.objects.filter(workflow_type=1)
	for choice in workflows:
		choices.append((choice.id, choice.name))
	return choices

def start_workflow(request, pk):
	#Add meta execution workflow field
	userflow = get_object_or_404(Workflow, id = pk)
	f = [{"name": "MEW", "label": "Select Execution Workflow", "datatype": "choice", "choices": get_meta_workflows()}]
	if request.method == 'POST':
		form = CustomForm(f, request.POST, request.FILES)
		if form.is_valid():
			# print(form.data)
			execution_workflow = Workflow.objects.get(id=form.data['MEW'])
			print(userflow.name, execution_workflow.name)
			start_flow.send(sender=None, MetaFlow=execution_workflow, UserFlow=userflow)
			print("Form valid")
		else:
			print("Form invalid")
		return redirect('home')
	else:
		form = CustomForm(f)
	return render(request, 'select_mew.html', {"workflow": userflow, "user": request.user, "form": form})

def show_worklist(request):
	running_tasks = TaskExec.objects.exclude(state=5).exclude(state=6)
	running_tasks = [tsk for tsk in running_tasks if tsk.task.task_type == 1]
	user_tasks = list()
	for task in running_tasks:
		tsk = task
		print(tsk.task.name)
		try:
			user_tasks.append({"user_task": TaskExec.objects.get(id=task.data['user_task']), "meta_task": task})
		except:
			print("No user task found!! for ", task)

	print(user_tasks)
	if not request.user.is_superuser:
		roles = RoleAssign.objects.filter(user=request.user)
		user_tasks = list()
		for tsk in user_tasks:
			task = tsk.task
			if (task.role in roles) and (task.state != 5 or task.state != 6):
				user_tasks.append(tsk)
	else:
		tasks = user_tasks

	return render(request, "show_worklist.html", {"tasks": user_tasks, 'states': states})


def specify_workflow(request):
	user = request.user
	print(user.username)
	f = [{"name": "workflow_json", "label": "Upload a file", "datatype": "file"}]
	if request.method == 'POST':
		form = CustomForm(f, request.POST, request.FILES)
		if form.is_valid():
			# print(form.data, request.FILES)
			load_workflow(request.FILES['workflow_json'])
		else:
			print("Form invalid")
		return redirect('home')
	else:
		form = CustomForm(f)
	return render(request, "specify_workflow.html", {"form": form})

def load_roles(request):
	print("Loading roles...............")
	workflow_id = request.GET.get('workflow')
	workflow = Workflow.objects.get(pk=workflow_id)
	assert workflow is not None
	roles = list()
	for role in workflow.roles:
		roles.append(Role.objects.get(pk=role))
	return render(request, 'role_dropdown.html', {'roles': roles})


def next_task(request, pk):
	task_exec = get_object_or_404(TaskExec, id = pk)
	user_task = TaskExec.objects.get(id=task_exec.data['user_task'])
	print("Next task for execution is", user_task.task.name)
	assert task_exec is not None and user_task is not None
	user = request.user
	if request.method == 'POST':
		form = CustomForm(user_task.task.form, request.POST, request.FILES)
		if form.is_valid():
			user_task.data = {**form.data, **user_task.data}
			user_task.workflow_exec.data  = {**user_task.workflow_exec.data, **task_exec.data}
			user_task.save(), user_task.workflow_exec.save()
			start_task.send(sender=None, task_exec=task_exec)
			print("Form valid")
			print(form.data)
		else:
			print("Form invalid")
		return redirect('home')
	else:
		form = CustomForm(user_task.task.form)
	return render(request, 'next_task.html', {'task': user_task.task, 'form': form, 'user': request.user })
	# return render(request, 'next_task.html', {'form': form, 'user': request.user })

def assign_role(request):
	user = request.user
	if request.method == 'POST':
		form = RoleAssignmentForm(request.POST)
		if form.is_valid():
			print(form.data)
		else:
			print("Form invalid")
		return redirect('home')
	else:
		form = RoleAssignmentForm()
	return render(request, 'role_assign.html', {'form': form, 'user': user})
