from enum import Enum


class TaskStates(Enum):
    NOT_STARTED = "not started"
    STARTED = "started"
    READY = "ready"
    RUNNING = "running"
    FINISHED = "finished"