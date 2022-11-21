from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from user.models import Profile


class ActiveUserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated:
            Profile.objects.filter(user__id=request.user.id) \
                .update(last_activity=timezone.now())