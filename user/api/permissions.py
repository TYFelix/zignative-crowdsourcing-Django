from rest_framework.permissions import BasePermission

from user.models import Verification, Profile


class IsAuthorized(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            verified = Verification.objects.filter(user=request.user)
        else:
            verified = False
        return request.user and request.user.is_authenticated and verified.exists()

    message = "You need to log in and have your account verified."


class IsCompleted(BasePermission):

    def has_permission(self, request, view):

        profile = Profile.objects.filter(user=request.user)
        return profile.exists()

    message = "You need to complete the registration steps."



