from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset
from .models import Course, CourseSection


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'category', 'fullname', 'shortname', 'idnumber', 'summary', 'image',
            'format', 'enrollment_type', 'enrolment_key', 'max_students',
            'visible', 'startdate', 'enddate', 'completion_enabled', 'show_grades',
        ]
        widgets = {
            'startdate': forms.DateInput(attrs={'type': 'date'}),
            'enddate': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset('Basic Information',
                Row(Column('fullname', css_class='col-md-8'), Column('shortname', css_class='col-md-4')),
                Row(Column('category', css_class='col-md-6'), Column('idnumber', css_class='col-md-6')),
                'summary',
                'image',
            ),
            Fieldset('Enrollment Settings',
                Row(Column('enrollment_type', css_class='col-md-6'), Column('max_students', css_class='col-md-6')),
                'enrolment_key',
            ),
            Fieldset('Course Settings',
                Row(Column('format', css_class='col-md-4'), Column('startdate', css_class='col-md-4'), Column('enddate', css_class='col-md-4')),
                Row(Column('visible'), Column('completion_enabled'), Column('show_grades')),
            ),
            Submit('submit', 'Save Course', css_class='btn btn-primary mt-3'),
        )


class CourseSectionForm(forms.ModelForm):
    class Meta:
        model = CourseSection
        fields = ['name', 'summary', 'visible']
