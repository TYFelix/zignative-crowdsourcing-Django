from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django_countries import countries
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer, HTMLFormRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase
from django.conf import settings

from user.api.permissions import IsAuthorized
from user.api.serializers import ChangePasswordSerializer, RegisterSerializer, ForgotPasswordSerializer, \
    ResetPasswordSerializer, RegisterStep2Serializer, RegisterStep3Serializer, ResendSerializer, \
    TokenObtainPairSerializer, CountrySerializer
from user.models import Verification, Profile
from user.tokens import PasswordResetToken, password_reset_token, AccountVerificationToken




class CreateUserView(CreateAPIView):
    model = User.objects.all()
    serializer_class = RegisterSerializer

class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = TokenObtainPairSerializer

class RegisterStep2View(APIView):
    serializer_class=RegisterStep2Serializer
    permission_classes = [IsAuthenticated,IsAuthorized]

    def post(self, request,*args, **kwargs):
        image = request.data['image']
        country = request.data['country']
        print(country)
        serializer = RegisterStep2Serializer(data={"image":image,"country":country})
        if serializer.is_valid():
            try:
                Profile.objects.create(role="init",user=request.user,country=country)
            except:
                profile = Profile.objects.get(user=request.user)
                profile.delete()
                Profile.objects.create(role="init", user=request.user, country=country)

            return Response({"Profile":"Image and country saved successfully"}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterStep3View(APIView):
    serializer_class = RegisterStep3Serializer
    permission_classes = [IsAuthenticated,IsAuthorized]

    def post(self, request, *args, **kwargs):
        role = request.data["role"]
        if role == "customer":
            role = "client"
        serializer = RegisterStep3Serializer(data={"role":role})
        if serializer.is_valid():
            try:
                request.user.profile.role = serializer.data.get('role')
                request.user.profile.save()
            except:
                Profile.objects.create(role=serializer.data.get('role'), user=request.user)


            return Response({"Role": "OK"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyAccountView(APIView):
    def get(self,request,*args,**kwargs):
        token = kwargs["token"]
        base64 = kwargs["base64"]
        account_verification_token = AccountVerificationToken()

        try:
            decoded_base64 = force_text(urlsafe_base64_decode(base64))
            user = User.objects.get(username=decoded_base64)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_verification_token.check_token(user, token):
            try:
                user.verification.delete()
            except:
                pass
            Verification.objects.create(user=user)
            return Response({"account": "verifed"}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"Token": "Invalid Token"}, status=status.HTTP_406_NOT_ACCEPTABLE)

class ResendView(APIView):
    serializer_class = ResendSerializer

    def post(self,request,*args,**kwargs):
        username = request.data['username']
        serializer = ResendSerializer(data={"username":username})
        if serializer.is_valid():
            username = serializer.data.get('username')
            user = User.objects.get(username=username)
            send_verify_mail(user = user,request = request)
            return Response({"mail": "sended"}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryView(APIView):

    def get(self,request,*args,**kwargs):

        return Response(countries.countries)

class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer

    def post(self,request,*args,**kwargs):
        email = request.data['email']
        serializer = ForgotPasswordSerializer(data={"email":email})

        if serializer.is_valid():
            email = serializer.data.get('email')
            user = User.objects.get(email=email)

            ### Creating Reset Token
            password_reset_token = PasswordResetToken()
            token = password_reset_token.make_token(user)

            ### Username base64 encode
            base64 = urlsafe_base64_encode(force_bytes(user.username))

            hostname = request.get_host()

            verify_link = f"{hostname}/reset-password?token={base64}/{token}"

            message_html = render_to_string("email/api_reset_password.html", {"verify_link": verify_link,"user":user})

            ### Mail content with reset link
            message = f"Click the link below to reset your password \n {verify_link}"

            send_mail(subject="Reset Password", message=message, html_message=message_html, from_email='testmest5398@gmail.com',
                      recipient_list=[str(email)])

            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer

    def put(self,request,*args,**kwargs):
        base64 = kwargs["base64"]
        token = kwargs["token"]
        new_password = request.data['new_password']
        serializer = ResetPasswordSerializer(data={"new_password": new_password})

        try:
            decoded_base64 = force_text(urlsafe_base64_decode(base64))
            user = User.objects.get(username=decoded_base64)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if serializer.is_valid():
            if user is not None and password_reset_token.check_token(user, token):
                user.set_password(serializer.data.get("new_password"))
                user.save()
                update_session_auth_hash(request, user)  # Important!

                return Response(status=status.HTTP_200_OK)
            else:
                return Response({"token":"This token has expired or wrong token. "}, status=status.HTTP_408_REQUEST_TIMEOUT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UpdatePassword(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    def get_object(self):
        return self.request.user

    def put(self,request,*args, **kwargs):
        self.object = self.get_object()
        data = {
            "old_password" : request.data["old_password"],
            "new_password" : request.data["new_password"]
        }

        serializer = ChangePasswordSerializer(data=data)

        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({"old_password": "Wrong password"},status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status = status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_verify_mail(user,request):
    ### Creating  Token
    account_verification_token = AccountVerificationToken()
    token = account_verification_token.make_token(user)

    ### Username base64 encode
    base64 = urlsafe_base64_encode(force_bytes(user.username))

    if settings.MODE == "development":
        hostname = "http://127.0.0.1:8000"
    elif settings.MODE == "testing":
        hostname = "http://46.101.148.167"
    else:
        hostname = "https://zignative.com"
    hostname = request.get_host()
    ### Mail content with verification link
    verify_link = f"{hostname}/login?verify={base64}/{token}"
    message_html = render_to_string("email/api_confirm_account.html", {"verify_link": verify_link,"email":user.email,'user':user})
    message = render_to_string("email/verify.txt", {"verify_link": verify_link})

    send_mail(subject="Verify your account", message=message, html_message=message_html,
              from_email='testmest5398@gmail.com',
              recipient_list=[str(user.email)], fail_silently=False)