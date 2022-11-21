import re

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import User, update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_countries import countries
from django_countries.serializer_fields import CountryField
from rest_framework import serializers, exceptions
from rest_framework.serializers import Serializer
from django.utils.translation import gettext_lazy as _

# changing password
from rest_framework_simplejwt.serializers import PasswordField
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Profile, Verification
from user.tokens import AccountVerificationToken


class ChangePasswordSerializer(Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        fields = ("old_password", "new_password",)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ForgotPasswordSerializer(Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ('email',)

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError('This email address is not registered.')


class ResetPasswordSerializer(Serializer):
    new_password = serializers.CharField(required=True)

    class Meta:
        fields = ("new_password",)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ProfileRegisterSerializer(serializers.ModelSerializer):
    ROLE = (('designer', 'Designer'), ('client', 'Client'),('developer','Developer'),('init','Init'))
    role = serializers.ChoiceField(required=True, choices=ROLE)

    class Meta:
        model = Profile
        fields = ('role',)
class CountrySerializer(serializers.Serializer):

    country = serializers.ListField(source=countries)
    class Meta:
        fields = ("country",)

def send_verify_mail(user):
    ### Creating  Token
    account_verification_token = AccountVerificationToken()
    token = account_verification_token.make_token(user)

    ### Username base64 encode
    base64 = urlsafe_base64_encode(force_bytes(user.username))

    if settings.MODE == "development":
        hostname = "http://134.122.93.235"
    elif settings.MODE == "testing":
        hostname = "http://134.122.93.235"
    else:
        hostname = "https://zignative.com"

    ### Mail content with verification link
    verify_link = f"{hostname}/login?verify={base64}/{token}"
    message_html = render_to_string("email/api_confirm_account.html", {"verify_link": verify_link,"email":user.email,'user':user})
    message = render_to_string("email/verify.txt", {"verify_link": verify_link})

    send_mail(subject="Verify your account", message=message, html_message=message_html,
              from_email='testmest5398@gmail.com',
              recipient_list=[str(user.email)], fail_silently=False)


class TokenObtainSerializer(serializers.Serializer):
    username_field = get_user_model().USERNAME_FIELD

    default_error_messages = {
        'no_active_account': _('No active account found with the given credentials')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField()

    def validate(self, attrs):
        username = attrs[self.username_field]

        if re.match(r"[^@]+@[^@]+\.[^@]+", username):
            users = User.objects.filter(email__iexact=username)
            if len(users) > 0 and len(users) == 1:
                attrs[self.username_field] = users.first().username

        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )



        return {}

    @classmethod
    def get_token(cls, user):
        raise NotImplementedError('Must implement `get_token` method for `TokenObtainSerializer` subclasses')


class TokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        profile = Profile.objects.filter(user=self.user)
        if profile.exists():
            if profile.first().role == "init":
                data.update({"is_init": True})
            else:
                data.update({"is_init":False})
        else:
            data.update({"is_init": True})
        ver = Verification.objects.filter(user=self.user)
        if ver.exists():
            data.update({"is_confirmed":True})
        else:
            data.update({"is_confirmed":False})
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def validate(self, attr):
        validate_password(attr["password"])

        return attr

    def validate_email(self, email):
        email = email.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already registered')
        return email

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"]
        )
        user.set_password(validated_data["password"])
        user.save()

        send_verify_mail(user=user)

        return user


class RegisterStep2Serializer(Serializer):
    image = serializers.ImageField(required=True)
    country = CountryField()

    class Meta:
        model = User
        fields = ('image', 'country')


class ResendSerializer(Serializer):
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username',)

    def validate(self, attr):
        return attr


class RegisterStep3Serializer(Serializer):
    ROLE = (('designer', 'Designer'), ('client', 'Client'))
    role = serializers.ChoiceField(required=True, choices=ROLE)

    class Meta:
        model = Profile
        fields = ('role',)
