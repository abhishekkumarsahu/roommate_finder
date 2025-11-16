from django import forms
from .models import Agreement

class AgreementForm(forms.ModelForm):
    class Meta:
        model = Agreement
        fields = ['rent', 'deposit', 'start_date', 'end_date', 'clauses']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'clauses': forms.Textarea(attrs={'rows':4}),
        }
