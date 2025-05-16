from django import forms
from .models import Task
from datetime import date

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task description',
                'rows': 4
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().isoformat()  # Prevent selecting past dates
            })
        }
