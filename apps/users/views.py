from django.shortcuts import render

import logging

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import RegisterSerializer, UserSerializer

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from apps.users.ratelimit import RATE_LIMIT_RESPONSE

logger = logging.getLogger("users")


@method_decorator(ratelimit(key="ip", rate="5/m", block=False), name="create")
class RegisterViewSet(viewsets.ViewSet):
  permission_classes = [AllowAny]

  def create(self, request):
    if getattr(request, "limited", False):
        return RATE_LIMIT_RESPONSE

    logger.info("Registration attempt email=%s", request.data.get("email"))

    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()
    refresh = RefreshToken.for_user(user)

    logger.info("User registered email=%s", user.email)

    return Response(
      {
        "user": UserSerializer(user).data,
        "tokens": {
          "refresh": str(refresh),
          "access": str(refresh.access_token),
        },
      },
      status=status.HTTP_201_CREATED,
    )