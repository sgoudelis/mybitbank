from django import forms
from django.forms import CharField
from connections import connector
from transfer.forms import CoinAddress, CoinProviderId

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
    initial_provider_id = connector.config.keys()[0]
    account_name = CoinAccountName(required=True, initial="")
    provider_id = CoinProviderId(required=True, initial=initial_provider_id)
    
    def clean(self):
        cleaned_data = super(CreateAccountForm, self).clean()
        return cleaned_data
    
class SetAddressAliasForm(forms.Form):
    alias = forms.CharField(initial="", required=True)
    address = CoinAddress(initial="", required=True)
    
    def clean(self):
        cleaned_data = super(SetAddressAliasForm, self).clean()

        return cleaned_data
