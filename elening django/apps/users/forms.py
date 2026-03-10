from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import User, UserProfile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'bio', 'avatar',
                  'phone', 'city', 'country', 'timezone', 'lang',
                  'department', 'institution', 'url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            Row(
                Column('username', css_class='col-md-6'),
                Column('lang', css_class='col-md-6'),
            ),
            'bio',
            'avatar',
            Row(
                Column('phone', css_class='col-md-6'),
                Column('city', css_class='col-md-6'),
            ),
            Row(
                Column('country', css_class='col-md-6'),
                Column('timezone', css_class='col-md-6'),
            ),
            Row(
                Column('department', css_class='col-md-6'),
                Column('institution', css_class='col-md-6'),
            ),
            'url',
            Submit('submit', 'Save Profile', css_class='btn btn-primary'),
        )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['website', 'interests', 'linkedin', 'twitter', 'skype']
        widgets = {
            'interests': forms.Textarea(attrs={'rows': 3}),
        }
