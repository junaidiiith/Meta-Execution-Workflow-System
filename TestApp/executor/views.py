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
# Create your views here.

def get_start_task(workflow):
	task = Task.objects.filter(workflow=workflow.id, name='start')
	assert task is not None
	return task

def home(request):
	running = WorkflowExec.objects.all().exclude(state=5).exclude(state=6)    #Add current task attr before rendering
	
	for workflow_exec in running:
		task_execs = TaskExec.objects.filter(workflow_exec=workflow_exec).exclude(state=5).exclude(state=6)
		if task_execs:
			current_tasks = task_execs[0].task.name
			for task_exec in task_execs:
				current_tasks += ", "+ task_exec.task.name
			workflow_exec.current_tasks = current_tasks

	ready = Workflow.objects.all()
	return render(request, 'home.html', {'running': running, 'user': request.user, 'ready': ready})

def start_workflow(request, pk):
	workflow = get_object_or_404(Workflow, id = pk)
	start_flow.send(sender=None,flow=workflow)
	return home(request)

def show_worklist(request):
	running_tasks = TaskExec.objects.exclude(state=5).exclude(state=6)
	if not request.user.is_superuser:
		running_tasks = TaskExec.objects.exclude(state=5).exclude(state=6)
		roles = RoleAssign.objects.filter(user=request.user)
		tasks = list()
		for task_exec in running_tasks:
			task = task_exec.task
			if (task.role in roles) and (task.state != 5 or task.state != 6):
				tasks.append(task_exec)
	else:
		tasks = running_tasks

	return render(request, "show_worklist.html", {"tasks": tasks})


def show_executable(request):
	executable = Workflow.objects.filter(workflow_type=2)
	f = [{"name": "workflow_json", "label": "Upload a file", "datatype": "file"}]
	if request.method == 'POST':
		form = CustomForm(f, request.POST, request.FILES)
		if form.is_valid():
			print(form.data) #Add workflow in executing list
		else:
			print("invalid form")
		return redirect('home')
	else:
		form = CustomForm(f)

	return render(request, "show_executable.html", {"executable": executable})


def specify_workflow(request):
	return render(request, "specify_workflow.html")

def load_roles(request):
	workflow_id = request.GET.get('workflow')
	workflow = Workflow.objects.get(pk=workflow_id)
	assert workflow is not None
	roles = list()
	for role in workflow.roles:
		roles.append(Role.objects.get(pk=role))
	return render(request, 'role_dropdown.html', {'roles': roles})


def next_task(request, pk):
	task_exec = get_object_or_404(TaskExec, id = pk)
	workflow_exec = task_exec.workflow_exec
	assert task_exec is not None
	user = request.user
	if request.method == 'POST':
		form = CustomForm(task_exec.task.form, request.POST, request.FILES)
		if form.is_valid():
			task_exec.data = {**form.data, **task_exec.data}
			workflow_exec.data  = {**workflow_exec.data, **task_exec.data}
			start_task.send(sender=None, task_exec=task_exec, flow_exec=workflow_exec)
			print("Form valid")
			print(form.data)
		else:
			print("Form invalid")
		return redirect('home')
	else:
		form = CustomForm(task_exec.task.form)
	return render(request, 'next_task.html', {'task': task_exec, 'form': form, 'user': request.user })
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
