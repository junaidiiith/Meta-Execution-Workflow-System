from .models import *
import json

def load_workflow_attribs(attrs, workflow):
	w = Workflow()
	for attr in attrs:
		w.attr = workflow[attr]
	w.save()
	return w

def load_roles(workflow,flow):
	roles = workflow['roles']
	rls = list()
	r_ids = list()
	for role in roles:
		r = Role(name=role)
		r.save()
		rls.append(r)
		r_ids.append(r.id)
	flow.roles = r_ids
	flow.save()
	return rls

def load_conditions(attrs, conditions, flow):
	cnds = list()
	for condition in conditions:
		c = Condition(workflow=flow)
		for attr in attrs:
			c[attr] = condition[attr]
		c.save()
		cnds.append(c)
	return cnds

def load_tasks(attrs, tasks, flow, roles, conditions):
	tsks = list()
	for task in tasks:
		t = Task(workflow=flow)
		for attr in attrs:
			t.attr = task[attr]
		t.save()
		tsks.append(t)
	return tsks

def load_events(attrs, events, flow, tasks):
	evnts = list()
	task_dict = dict()
	for task in tasks:
		task_dict[task.name] = task
	for event in events:
		e = Event(task=task_dict[event['task']])
		for attr in attrs:
			e.attr = event[attr]
		e.save()
		evnts.append(e)
	return evnts

def load_rules(rules, flow, conditions, events, tasks, task_json):
	rls = list()
	condition_dict, event_dict, task_dict = dict(), dict(), dict()
	for condition in conditions:
		condition_dict[condition.name] = condition
	for event in events:
		event_dict[event.name] = event
	for rule in rules:
		r = Rule(name=rule['name'], workflow=flow, event=event_dict[rule['event']], condition=condition)
		r.save()
		rls.append(r)
	return rls

def add_rule_expressions(w_tasks, rules, tasks):
	rules_dict = dict()
	for rule in rules:
		rules_dict[rule.name] = rule
	for task in tasks:
		tasks_dict[task.name] = task

	for task in w_tasks:
		rule_expression = task['event_expression']
		gate = rule_expression['gate']
		rules = rule_expression['expression']
		rule_ids = list()
		for rule in rules:
			rule_ids.append(rules_dict[rule['name']].id)

		task_dict[task].rule_expression = {"gate": gate, "rules": rule_ids}
		task_dict[task].save()

def load_workflow(workflow):
	workflow = json.load(open(workflow))
	w_attribs = ['name','workflow_type','description','constants','resources']
	c_attribs = ['name', 'operator', 'operand', 'constant']
	t_attribs = ['name','description','role','input_params','output_params','data','form','handler','task_type']
	e_attribs = ['name','state']
	flow = load_workflow_attribs(w_attribs, workflow)
	roles = load_roles(flow, workflow['roles'])
	conditions = load_conditions(c_attribs, workflow['conditions'], flow)
	tasks = load_tasks(t_attribs, workflow['tasks'], flow, roles, conditions)
	events = load_events(e_attribs, workflow['events'], flow, tasks)
	rules = load_rules(flow, workflow['rules'], conditions, events, tasks, workflow)
	add_rule_expressions(workflow['tasks'], rules, tasks)
	print("Successfully loaded workflow")