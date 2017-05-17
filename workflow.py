import json
class workflow:
	def __init__(self,spec):
		self.spec = spec
		ws = parse_json(spec)
		self.tasks = ws.tasks
		self.eca_rules = ws.eca_rules
		self.roles = ws.roles
		self.agents = ws.agents

	def parse_json(self,spec):
		return json.loads(spec)
