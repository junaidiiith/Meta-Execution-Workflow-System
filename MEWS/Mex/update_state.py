import add_to_db


class UpdateState:

    def __init__(self,task,**kwargs):

        sw = kwargs.get('sw').id
        ew = task.workflow.id
        q = 'update executions set E_state="Running" where Executor_id='+ew+' and Executed_id='+sw
        add_to_db.AddToDb(table='executions',username='root',password='123',query=q,database='MEWS')
