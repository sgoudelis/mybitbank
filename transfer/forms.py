from django import forms
from django.forms import CharField

class CoinAddress(CharField):
    def validate(self, value):
        if value == "":
            raise forms.ValidationError("This in not a valid address")
        
class SendCurrencyForm(forms.Form):
    from_address = CoinAddress()
    to_address = CoinAddress()
    comment = forms.CharField(max_length=500)
    amount = forms.CharField(max_length=100)