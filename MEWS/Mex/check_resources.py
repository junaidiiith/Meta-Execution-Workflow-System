class CheckResources:
    def __init__(self,**kwargs):
        tasks = kwargs.get('sw_tasks')
        for task in tasks:
            try:
                parts = task.agent.rsplit('.', 1)
                m = __import__(parts[0])
            except:
                return "Resources not found for" + task.description
