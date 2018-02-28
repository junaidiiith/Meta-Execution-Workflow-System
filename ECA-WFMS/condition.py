import operator

ops = {
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
        '>=': operator.ge,
        '>': operator.gt
    }
class Condition(object):
    def __init__(self, condition):
        self._condition = condition

    def check(self, data):
        operand = data[self.condition['operand']]
        op = self.condition['operator']
        constant = self.condition['constant']

        operation = ops.get(op)
        return operation(operand, constant)

    @property
    def condition(self):
        return self._condition
