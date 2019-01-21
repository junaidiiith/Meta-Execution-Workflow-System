from django import forms
from specifier.models import *
from users.models import *

def check(field,attr):
	try:
		return field[attr]
	except:
		return ''

class CustomForm(forms.Form):  
	def __init__(self, fields, *args, **kwargs):  
		super(CustomForm, self).__init__(*args, **kwargs)  
		for field in fields:
			if field['datatype'] == 'int':  
			    self.fields[field['name']] = forms.IntegerField()  
			elif field['datatype'] == 'char':  
			    self.fields[field['name']] = forms.CharField(max_length=field['max_length'], label=check(field,'label'))  
			elif field['datatype'] == 'boolean': 
			    self.fields[field['name']] = forms.BooleanField(required=False, label=check(field,'label'))
			elif field['datatype'] == 'text': 
			    self.fields[field['name']] = forms.TextField(label=check(field,'label'))
			elif field['datatype'] == 'file': 
			    self.fields[field['name']] = forms.FileField(label=check(field,'label'))
			elif field['datatype'] == 'choice':
				self.fields[field['name']] = forms.ChoiceField(choices=field['choices'])
			elif field['datatype'] == 'email':
				self.fields[field['name']] = forms.EmailField()
			elif field['datatype'] == 'float':
				self.fields[field['name']] = forms.FloatField()

class RoleAssignmentForm(forms.ModelForm):
	class Meta:
		model = RoleAssign
		fields = ('workflow','role','user')

		def __init__(*args, **kwargs):
			super().__init__(*args, **kwargs)
			self.fields['role'].queryset = Role.objects.none()
			self.fields['user'].queryset = CustomUser.objects.none()
		