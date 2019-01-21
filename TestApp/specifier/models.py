from django_mysql.models import JSONField, Model
from django.db import models
from executor.choices import states
from TestApp import settings


class Workflow(Model):
	name = models.CharField(max_length=50)
	workflow_type = models.IntegerField(choices = ((1, 'meta'),(2,'non-meta')), default=1)
	description = models.TextField()
	constants = JSONField()
	roles = JSONField()
	resources = JSONField()

	def __str__(self):
		return self.name+": "+self.description


class Role(Model):
	name = models.CharField(max_length=50)
	def __str__(self):
		return self.name
		
class Task(Model):
	name = models.CharField(max_length=50)
	task_type = models.IntegerField(choices = ((1, 'meta'),(2,'non-meta')), default=1)
	description = models.TextField()
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='tasks')
	role = models.ForeignKey(Role, null=True, on_delete=models.SET_NULL)
	input_params = JSONField()
	output_params = JSONField()
	data = JSONField()
	form = JSONField()
	handler = JSONField()
	rule_expression = JSONField()

class RoleAssign(Model):
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE )
	role = models.ForeignKey(Role, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Condition(Model):
	name = models.CharField(max_length=50)
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
	operand = JSONField()
	operator = JSONField()
	constant = JSONField()

class Event(Model):
	name = models.CharField(max_length=50)
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	state = models.IntegerField(choices = states, default=1)

class Rule(Model):
	name = models.CharField(max_length=50)
	workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	condition = models.ForeignKey(Condition, on_delete=models.CASCADE)

class Task_Rule(Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	rule = models.ForeignKey(Rule, on_delete=models.CASCADE)