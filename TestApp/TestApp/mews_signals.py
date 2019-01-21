from django.core import signals
from django.dispatch import receiver, Signal


start_flow = Signal(providing_args=['flow'])
end_flow = Signal(providing_args=['flow'])
stop_flow = Signal(providing_args=['flow'])

start_task = Signal(providing_args=['task','flow_exec'])
assign_user_task = Signal(providing_args=['task_exec','flow_exec'])
execute_task = Signal(providing_args=['task_exec','flow_exec'])
end_task = Signal(providing_args=['task_exec','flow_exec'])
stop_task = Signal(providing_args=['task_exec','flow_exec'])