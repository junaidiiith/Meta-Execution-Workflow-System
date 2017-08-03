from uuid import uuid4


class Condition:
    __slots__ = ['id', '_description', 'event_id', 'type']

    def __init__(self, event_id, desc=None, type=None):
        self.id = uuid4()
        self.type = type
        self._description = desc
        self.event_id = event_id


class ArithmeticEqualityCondition:
    def __init__(self, operand, operator, constant ):
        self.operator = operator
        self.operand = operand
        self.constant = constant

    def get_condition(self):
        if self.operator.tolower() == "equal" or self.operator == '=' or self.operator == '==':
            self.condition = str(self.operand) + " == " + str(self.constant)
        elif self.operator.tolower() == "lte" or self.operator == '<=':
            self.condition = str(self.operand) + " <= " + str(self.constant)

        elif self.operator.tolower() == "gte" or self.operator == '>=':
            self.condition = str(self.operand) + " >= " + str(self.constant)

        elif self.operator.tolower() == "lt" or self.operator == '<':
            self.condition = str(self.operand) + " < " + str(self.constant)

        elif self.operator.tolower() == "g" or self.operator == '>':
            self.condition = str(self.operand) + " > " + str(self.constant)
        else:
            self.condition = None


class Dbcondition:

        def __init__(self, table, attribute, id):
            self.table = table
            self.attribute = attribute
            self.id = id

        def inserted(self):
            return "Check for insert query"

        def deleted(self):
            return "Check for delete query"

        def updated(self):
            return 'Check for update query'
