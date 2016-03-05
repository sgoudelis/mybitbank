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

from mybitbank.libs.connections import connector
from mybitbank.apps.transfer.forms import CoinAddress, CoinProviderId
from mybitbank.libs import misc

class CoinAccountName(CharField):
    def validate(self, value):
        super(CharField, self).validate(value)

class CoinCurrency(CharField):
    def validate(self, value):
        super(CharField, self).validate(value)
        supported_currencies = connector.services.keys()
        if value not in supported_currencies:
            raise forms.ValidationError("This currency is not supported: %s" % value)

class AddAddressBookForm(forms.Form):
    name = forms.CharField(required=True, initial="")
    address = CoinAddress(required=True, initial="")
    provider_id = CoinProviderId(required=True, initial=misc.getInitialProviderId(connector))
    comment = forms.CharField(required=False, initial="")

    def clean_address(self):
        address = self.cleaned_data['address']
        return address.strip()
    
    def clean(self):
        cleaned_data = super(AddAddressBookForm, self).clean()
        return cleaned_data
    
