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
    