import re

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django import  forms

from user.models import Profile

class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=50)
    password = forms.CharField(required=True, max_length=50,widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):

        super(LoginForm, self).__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}


    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)


        if not user:
            raise forms.ValidationError('Email or password wrong')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if re.match(r"[^@]+@[^@]+\.[^@]+", username):
            users = User.objects.filter(email__iexact=username)
            if len(users) > 0 and len(users) == 1:
                return users.first().username
        return username

class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username','email', 'password1', 'password2', )


    def __init__(self,*args, **kwargs):

        super(RegisterForm, self).__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field in self.fields:
            self.fields[field].widget.attrs={'class':'form-control'}

    #Check if your email is registered in the system
    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = email.lower()
        if User.objects.filter(email=email).exists():

            raise forms.ValidationError('This email is already registered')
        return email

    #Check if your password match
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2

class PasswordResetForm(SetPasswordForm):

    def __init__(self,*args, **kwargs):

        super(PasswordResetForm, self).__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field in self.fields:
            self.fields[field].widget.attrs={'class':'form-control'}


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ( 'username', 'email')

    def __init__(self,user, *args, **kwargs):
        self.user = user
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}


        self.fields["email"].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = email.lower()
        if User.objects.filter(email=email).exists():
            if email != self.user.email:
                raise forms.ValidationError('A user with that email already exists.')
        return email
    def clean_username(self):
        username = self.cleaned_data.get('username')
        username = username.lower()
        if User.objects.filter(username=username).exists():
            if username != self.user.username:
                raise forms.ValidationError('A user with that username already exists.')
        return username

class ProfileUpdateForm(forms.ModelForm):
    languages = forms.MultipleChoiceField(widget=forms.SelectMultiple,
                                          choices=settings.LANGUAGES,help_text="Hold down “Control”, or “Command” on a Mac, to select more than one.")
    class Meta:
        model=Profile
        fields = ( 'cover_photo','photo','bio','country','is_available','languages')
    def __init__(self,user,*args, **kwargs):
        self.user = user
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)

        self.fields["bio"].widget.attrs={'row':'5'}
        self.fields["languages"].required=False
        self.fields["cover_photo"].widget.attrs={'url':'/members/upload_cover'}

