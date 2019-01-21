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
# Create your views here.

def get_start_task(workflow):
	task = Task.objects.filter(workflow=workflow.id, name='start')
	assert task is not None
	return task

def home(request):
	ready = Workflow.objects.all()
	running = WorkflowExec.objects.all()    #Add current task attr before rendering
	return render(request, 'home.html', {'running': running, 'ready' : ready , 'user': request.user})

def start_workflow(request, pk):
	workflow = get_object_or_404(Workflow, id = pk)
	start_flow.send(sender=None,workflow=workflow)
	return home(request)


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
	workflow_exec = WorkflowExec.objects.get(pk=task_exec.workflow_exec)
	assert task_exec is not None
	user = request.user
	if request.method == 'POST':
		form = CustomForm(f, request.POST, request.FILES)
		if form.is_valid():
			task_exec.data = {**form.data, **task_exec.data}
			workflow_exec.data  = {**workflow_exec.data, **task_exec.data}
			start_workflow_task.send(sender=None, task_exec=task_exec, workflow_exec=workflow_exec)
			print("Form valid")
			print(form.data)
		else:
			print("Form invalid")
		return redirect('home')
	else:
		form = CustomForm(f)
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
