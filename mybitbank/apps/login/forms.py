from django import forms
from django.forms import CharField

class UsernameField(CharField):
    def validate(self, value):
        super(CharField, self).validate(value)
        if value == "":
            raise forms.ValidationError("Please enter a username")

class PasswordField(CharField):
    def validate(self, value):
        super(CharField, self).validate(value)
        if value == "":
            raise forms.ValidationError("Please enter a password")

class LoginForm(forms.Form):
    username = UsernameField(initial="")
    password = PasswordField()
    remember = forms.BooleanField(required=False)
    next_url = forms.CharField(required=False)
    
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        #username = cleaned_data.get('username', "")
        #password = cleaned_data.get('password', "")
        #remember = cleaned_data.get('remember', False)
        #next_url = cleaned_data.get('next_url', "")
        
        return cleaned_data