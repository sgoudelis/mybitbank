from django import forms

class SendCurrencyForm(forms.Form):
    account_address_from = forms.CharField(max_length=100)
    account_address_to = forms.CharField(max_length=100)
    amount = forms.CharField(max_length=100)