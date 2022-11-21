from django import forms

from designer.models import Work
from home.models import Contact


class WorkForm(forms.ModelForm):

    class Meta:
        model = Work
        fields = ('image',)


class RequestForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('subject', 'description', 'file')

    def __init__(self,  *args, **kwargs):

        super(RequestForm, self).__init__(*args, **kwargs)


class AnonUserRequestForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('role','email','subject', 'description', 'file')

    def __init__(self,  *args, **kwargs):
        super(AnonUserRequestForm, self).__init__(*args, **kwargs)
        self.fields["role"].required = True
        self.fields["email"].required = True


