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
from django.forms import CharField, IntegerField

from mybitbank.libs.connections import connector
from mybitbank.libs import misc

class CoinAccount(CharField):
    def validate(self, value):
        super(CharField, self).validate(value)

class CoinAddress(CharField):
    def validate(self, value):
        super(CharField, self).validate(value)
        if value == "":
            raise forms.ValidationError("Please provide a valid address")
        
        if len(value) < 27 or 34 > len(value):
            raise forms.ValidationError("Please provide a valid address")
            
class CoinAmount(CharField):
    def to_python(self, value):
        if not misc.isFloat(value):
            raise forms.ValidationError("Please provide a valid amount eg. 12.3456789")
        
        return float(value)
    
    def validate(self, value):
        super(CharField, self).validate(value)
        if not misc.isFloat(value):
            raise forms.ValidationError("Please provide a valid amount eg. 12.3456789")
        
        if value == 0 or value < 0:
            raise forms.ValidationError("Please provide a valid amount eg. 12.3456789")

class CoinCurrency(CharField):
    def validate(self, value):
        super(CharField, self).validate(value)
        supported_currencies = connector.services.keys()
        if value not in supported_currencies:
            raise forms.ValidationError("This currency is not supported: %s" % value)

class CoinProviderId(IntegerField):
    def validate(self, value):
        super(IntegerField, self).validate(value)
        if value not in connector.config.keys():
            raise forms.ValidationError("This currency provider id is not supported: %s" % value)
        
    def to_python(self, value):
        try:
            return int(value)
        except:
            return 0
        
class SendCurrencyForm(forms.Form):
    initial_provider_id = connector.config.keys()[0]
    
    from_account = CoinAccount(initial="")
    to_address = CoinAddress(initial="")
    to_account = CoinAccount(initial="", required=False)
    comment = forms.CharField(initial="", required=False)
    comment_to = forms.CharField(initial="", required=False)
    amount = CoinAmount(initial=0, required=True)
    provider_id = CoinProviderId(required=True, initial=initial_provider_id)
    passphrase = forms.CharField(initial="", required=False)
    
    def clean(self):
        cleaned_data = super(SendCurrencyForm, self).clean()
        # from_address = cleaned_data.get('from_address', "")
        # to_address = cleaned_data.get('to_address', "")
        
        # if from_address == to_address and (from_address and to_address):
        #    raise forms.ValidationError("You cannot move from and to the same account/address")
        
        return cleaned_data
