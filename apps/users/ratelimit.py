from rest_framework.response import Response
from rest_framework import status

RATE_LIMIT_RESPONSE = Response(
  {"detail": "Too many requests. Try again later!"},
  status=status.HTTP_429_TOO_MANY_REQUESTS,
)