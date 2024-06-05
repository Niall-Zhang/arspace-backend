from django.utils import timezone
from django.contrib.auth import get_user_model


class LastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            try:
                user = get_user_model().objects.get(pk=request.user.pk)
                user.last_seen = timezone.now()
                user.save()
            except get_user_model().DoesNotExist:
                pass  # Handle the case where the user does not exist

        return response
