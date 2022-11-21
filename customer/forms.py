from django import  forms
from django_countries.data import COUNTRIES
from django_countries.fields import CountryField

from customer.models import Poll


class CountryForm(forms.Form):
    country = CountryField().formfield()
    def __init__(self,*args, **kwargs):

        super(CountryForm, self).__init__(*args, **kwargs)

        self.fields["country"].widget.attrs={'class':'form-control','name':'country'}
        self.fields["country"].required = True

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ["title","content"]
