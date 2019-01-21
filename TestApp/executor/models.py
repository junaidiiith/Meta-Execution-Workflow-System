from django_mysql.models import JSONField, Model
from django.db import models
from executor.choices import states
from specifier.choices import objects
from specifier.models import *
import uuid
from TestApp import settings

class WorkflowExec(Model):
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
	state = models.IntegerField(choices = states, default=1)
	data = JSONField()

class TaskExec(Model):
	workflow_exec = models.ForeignKey(WorkflowExec, on_delete=models.CASCADE)
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	state = models.IntegerField(choices= states, default=1)
	data = JSONField()

class Worklist(Model):
	task = models.ForeignKey(TaskExec, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class EventDB(Model):
	object_type = models.IntegerField(choices = objects)
	object_id = models.IntegerField(primary_key=False, default=uuid.uuid4)
	state = models.IntegerField(choices = states, default=1)