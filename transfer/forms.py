from django import forms
from django.forms import CharField
import generic
from connections import connector

class CoinAddress(CharField):
    def validate(self, value):
        if value == "":
            raise forms.ValidationError("Please provide a valid address")

class CoinAmount(CharField):
    def to_python(self, value):
        if not generic.isFloat(value):
            raise forms.ValidationError("Please provide a valid address")
        
        return float(value)
    
    def validate(self, value):
        if not generic.isFloat(value):
            raise forms.ValidationError("Please provide a valid amount")

class CoinCurrency(CharField):
    def validate(self, value):
        supported_currencies = connector.services.keys()
        if value not in supported_currencies:
            raise forms.ValidationError("This currency is not supported: %s" % value)

class SendCurrencyForm(forms.Form):
    from_address = CoinAddress(initial="")
    to_address = CoinAddress(initial="")
    comment = forms.CharField(initial="", required=False)
    comment_to = forms.CharField(initial="", required=False)
    amount = CoinAmount(initial=0)
    selected_currency = CoinCurrency(initial="")
    passphrase = forms.CharField(initial="", required=False)
    
    def clean(self):
        cleaned_data = super(SendCurrencyForm, self).clean()
        from_address = cleaned_data.get('from_address', "")
        to_address = cleaned_data.get('to_address', "")
        comment = cleaned_data.get('comment', "")
        amount = cleaned_data.get('amount', 0)
        selected_currency = cleaned_data.get('selected_currency',"")
        passphrase = cleaned_data.get('passphrase',"")
        
        if from_address == to_address and (from_address and to_address):
            raise forms.ValidationError("You cannot move from and to the same account/address")
        
        return cleaned_data