from uuid import uuid4


class Tasks:
    def __init__(self,*args, **kwargs):
        self.type = 'user'

    def create_new_record(self):
        data = dict()
        username = input('Enter the name of the student')
        cgpa = input('Enter the CGPA')
        dob = input('Enter the birth date')
        id = uuid4()
        data['username'] = username
        data['CGPA'] = cgpa
        data['Date of birth'] = dob
        data['id'] = id

        return data

    def check_cgpa(self, constant, *args, **kwargs):
        return kwargs['cgpa'] >= constant

    def call_interview(self, name):
        return "Candidate ", name, "called for interview"

