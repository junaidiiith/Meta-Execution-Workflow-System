from .models import *
import json

def load_workflow_attribs(attrs, workflow):
    w = Workflow()
    for attr in attrs:
        setattr(w,attr,workflow[attr])
    w.save()
    return w

def load_roles(flow,roles):
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
            setattr(c,attr,condition[attr])
        c.save()
        cnds.append(c)
    return cnds

def load_tasks(attrs, tasks, flow, roles, conditions):
    tsks = list()
    role_dict = dict()
    for role in roles:
        role_dict[role.name] = role

    for task in tasks:
        t = Task(workflow=flow)
        for attr in attrs:
            if attr != 'role':
                setattr(t, attr, task[attr])
            else:
                setattr(t,attr, role_dict[task['role']])
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
            setattr(e, attr, event[attr])
        e.save()
        evnts.append(e)
    return evnts

def load_rules(rules, flow, conditions, events):
    rls = list()
    condition_dict, event_dict = dict(), dict()
    for condition in conditions:
        condition_dict[condition.name] = condition
    condition_dict[''] = "NULL"
    for event in events:
        event_dict[event.name] = event
    for rule in rules:
        r = Rule(name=rule['name'], workflow=flow, event=event_dict[rule['event']])
        if len(rule['condition']):
            r.condition = condition_dict[rule['condition']] 
        r.save()
        rls.append(r)
    return rls

def load_task_rule_association(tasks, rules, tasks_json):
    rules_dict,task_dict = dict(),dict()
    for rule in rules:
        rules_dict[rule.name] = rule
    # print(rules_dict)
    for task in tasks:
        task_dict[task.name] = task

    for task in tasks_json:
        rls = list()
        if task['rule_expression']:
            expression = task['rule_expression']

            for rule in expression['rules']:
                rls.append(rules_dict[rule].id)
                Task_Rule(task=task_dict[task['name']], rule=rules_dict[rule]).save()
            tsk = task_dict[task['name']]
            tsk.rule_expression = {"gate": expression['gate'], "rules": rls}
            tsk.save()


def load_workflow(workflow):
    workflow = json.load(open(workflow))
    w_attribs = ['name','workflow_type','description','constants','resources']
    c_attribs = ['name', 'operator', 'operand', 'constant']
    t_attribs = ['name','description', 'role', 'task_type', 'input_params','output_params','form','handler','task_type']
    e_attribs = ['name','state']
    flow = load_workflow_attribs(w_attribs, workflow)
    roles = load_roles(flow, workflow['roles'])
    conditions = load_conditions(c_attribs, workflow['conditions'], flow)
    tasks = load_tasks(t_attribs, workflow['tasks'], flow, roles, conditions)
    events = load_events(e_attribs, workflow['events'], flow, tasks)
    rules = load_rules(workflow['rules'], flow, conditions, events)
    load_task_rule_association(tasks, rules, workflow['tasks'])
    print("Successfully loaded workflow")

def flush_database():
    tables = [Workflow,Role,Event,Condition,Rule, Task_Rule,Task]
    for table in tables: 
        for obj in table.objects.all(): 
            obj.delete()

flush_database()
load_workflow('KnowledgeBase/admissions.json')
load_workflow('KnowledgeBase/mew.json')
# load_workflow('KnowledgeBase/msw.json')


# from TestApp.mews_signals import *
# from uuid import uuid4
# from executor.models import *
# from specifier.models import *
# from django.dispatch import receiver
# from executor.utils import *
# from specifier.utils import *
# from executor.event_handlers import *
# MW = Workflow.objects.all()[1]
# UW = Workflow.objects.all()[0]
# start_flow.send(None, MetaFlow=MW, UserFlow=UW)
# for taskexec in TaskExec.objects.all().exclude(state=5).exclude(state=6):
#     if taskexec.task.task_type == 1:
#         start_task.send(None, task_exec=taskexec)
