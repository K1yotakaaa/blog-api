from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.ratelimit import RATE_LIMIT_RESPONSE


@method_decorator(ratelimit(key="ip", rate="10/m", block=False), name="post")
class RateLimitedTokenObtainPairView(TokenObtainPairView):
  def post(self, request, *args, **kwargs):
    if getattr(request, "limited", False):
      return RATE_LIMIT_RESPONSE
    return super().post(request, *args, **kwargs)