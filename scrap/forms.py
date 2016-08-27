from django import forms


class UrlForm(forms.Form):
    url = forms.CharField(label='', max_length=2000)