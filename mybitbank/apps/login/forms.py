"""
The MIT License (MIT)

Copyright (c) 2016 Stratos Goudelis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

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
        # username = cleaned_data.get('username', "")
        # password = cleaned_data.get('password', "")
        # remember = cleaned_data.get('remember', False)
        # next_url = cleaned_data.get('next_url', "")
        
        return cleaned_data
