class Execute:
    def __init__(self,**kwargs):
        sw_tasks = kwargs.get('sw_tasks')

        out = []
        for task in sw_tasks:
            out.append(task.execute())

        return out,None