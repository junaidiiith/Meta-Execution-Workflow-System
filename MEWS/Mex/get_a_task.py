class GetTask:
    def __init__(self, task, **kwargs):
        if not kwargs.get('sw_tasks'):
            return kwargs.get('sw').start

        return kwargs.get('sw_tasks')

