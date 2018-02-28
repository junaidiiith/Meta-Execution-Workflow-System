class Specifier(object):
    def __init__(self):
        self.begin()

    def begin(self):
        print('Initiating workflow specification')
        print('Setting up database tables')
        #set database
        W = Workflow()
