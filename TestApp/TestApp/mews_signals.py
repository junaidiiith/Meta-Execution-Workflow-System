from django.core import signals
from django.dispatch import receiver, Signal


start_flow = Signal(providing_args=['MetaFlow', 'UserFlow', 'MetaExec'])
end_flow = Signal(providing_args=['flow'])
stop_flow = Signal(providing_args=['flow'])

start_task = Signal(providing_args=['task_exec'])
assign_user_task = Signal(providing_args=['task_exec'])
execute_task = Signal(providing_args=['task_exec'])
end_task = Signal(providing_args=['task_exec'])
stop_task = Signal(providing_args=['task_exec'])