import generic
from django import forms
from django.forms import CharField
from connections import connector
from transfer.forms import CoinAddress

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
    
    try:
        # try to get the last currency in the services list
        initial_currency = connector.services.keys()[-1]
    except:
        initial_currency = ""
    
    name = forms.CharField(required=True, initial="")
    address = CoinAddress(initial="")
    currency = CoinCurrency(required=True, initial=initial_currency)
    comment = forms.CharField(required=False, initial="")
    
    def clean(self):
        cleaned_data = super(AddAddressBookForm, self).clean()
        name = cleaned_data.get('name', "")
        address = cleaned_data.get('address', "")
        currency = cleaned_data.get('currency', self.initial_currency)
        comment = cleaned_data.get('comment', "")
        
        # clean data ?
        return cleaned_data