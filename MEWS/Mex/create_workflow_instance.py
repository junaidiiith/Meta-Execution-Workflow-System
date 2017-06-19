import add_to_db


class CreateWfInstance:

    def __init__(self,task,**kwargs):

        table = 'create table executions (Executor varchar(100), Executor_id int, Executed varchar(100), Executed_id int,  E_state varchar(100), S_state varchar(100, primary key(Executor, Executed)'
        sw = kwargs.get('sw').description
        ew = task.workflow.description
        sw_id = kwargs.get('sw').id
        ew_id = task.workflow.id
        e_state = "READY"
        s_state = "READY"
        q = 'insert into executions values ('+ ew +','+ ew_id +','+ sw +','+ sw_id+','+ e_state+','+ s_state+')'
        add_to_db.AddToDb(table=table,username='root',password='123',query=q,database='MEWS')

        if task.manual:
            table = 'create table worklist (role varchar(100), task int)'
            owner = task.owner
            q = 'insert into worklist values' +'('+owner+','+ task.id+')'
            add_to_db.AddToDb(table=table, username='root', password='123', query=q, database='MEWS')

