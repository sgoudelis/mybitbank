import generic
from django import forms
from django.forms import CharField
from connections import connector

class CoinAccountName(CharField):
    def validate(self, value):
        super(CharField, self).validate(value)

class CoinCurrency(CharField):
    def validate(self, value):
        super(CharField, self).validate(value)
        supported_currencies = connector.services.keys()
        if value not in supported_currencies:
            raise forms.ValidationError("This currency is not supported: %s" % value)

class CreateAccountForm(forms.Form):
    
    try:
        # try to get the last currency in the services list
        initial_currency = connector.services.keys()[-1]
    except:
        initial_currency = ""
    
    account_name = CoinAccountName(required=True, initial="")
    currency = CoinCurrency(required=True, initial=initial_currency)
    
    def clean(self):
        cleaned_data = super(CreateAccountForm, self).clean()
        account_name = cleaned_data.get('account_name', "")
        currency = cleaned_data.get('currency', "")
        
        # clean data ?
        
        return cleaned_data