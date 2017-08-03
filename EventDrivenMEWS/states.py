from enum import Enum


class TaskStates(Enum):
    NOT_STARTED = "Not yet started"
    READY = "Ready"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"