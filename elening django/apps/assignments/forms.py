from django import forms
from .models import Submission, AssignmentGrade


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['online_text', 'file']


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentGrade
        fields = ['grade', 'feedback', 'released']
        widgets = {
            'grade': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
