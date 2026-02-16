import json
import logging

import redis
from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from apps.blog.models import Comment, Post, PostStatus
from apps.blog.permissions import IsOwnerOrReadOnly
from apps.blog.serializers import CommentSerializer, PostSerializer
from apps.users.ratelimit import RATE_LIMIT_RESPONSE

logger = logging.getLogger("blog")

POST_LIST_CACHE_KEY = "post_list_published_v1"
POST_LIST_TTL_SECONDS = 60

COMMENTS_CHANNEL = "comments"


def safe_cache_delete(key: str) -> None:
  try:
    cache.delete(key)
  except Exception as exc:
    logger.warning("Cache delete failed key=%s err=%s", key, exc)


def get_redis_url() -> str:
  cache_conf = settings.CACHES.get("default", {})
  redis_url = cache_conf.get("LOCATION")
  if not redis_url:
    raise RuntimeError("Redis is not configured: missing CACHES['default']['LOCATION']")
  return redis_url


@method_decorator(ratelimit(key="user", rate="20/m", block=False), name="create")
class PostViewSet(viewsets.ModelViewSet):
  serializer_class = PostSerializer
  lookup_field = "slug"

  def get_queryset(self):
    qs = Post.objects.select_related("author", "category").prefetch_related("tags")
    if self.action in ("list", "retrieve"):
      return qs.filter(status=PostStatus.PUBLISHED)
    return qs

  def get_permissions(self):
    if self.action in ("list", "retrieve"):
      return [AllowAny()]
    return [IsAuthenticated(), IsOwnerOrReadOnly()]

  def list(self, request, *args, **kwargs):
    cached = cache.get(POST_LIST_CACHE_KEY)
    if cached is not None:
      return Response(cached)
      
    response = super().list(request, *args, **kwargs)
    cache.set(POST_LIST_CACHE_KEY, response.data, timeout=POST_LIST_TTL_SECONDS)
    return response

  def create(self, request, *args, **kwargs):
    if getattr(request, "limited", False):
      return RATE_LIMIT_RESPONSE

    try:
      return super().create(request, *args, **kwargs)
    except IntegrityError:
      return Response(
        {"detail": "Post with this slug already exists."},
        status=status.HTTP_400_BAD_REQUEST,
      )

  def perform_create(self, serializer):
    logger.info("Post create attempt user_id=%s", self.request.user.id)
    post = serializer.save(author=self.request.user)
    safe_cache_delete(POST_LIST_CACHE_KEY)
    logger.info("Post created slug=%s", post.slug)

  def perform_update(self, serializer):
    post = serializer.save()
    safe_cache_delete(POST_LIST_CACHE_KEY)
    logger.info("Post updated slug=%s", post.slug)

  def perform_destroy(self, instance):
    slug = instance.slug
    instance.delete()
    safe_cache_delete(POST_LIST_CACHE_KEY)
    logger.info("Post deleted slug=%s", slug)

  @action(detail=True, methods=["get", "post"], url_path="comments")
  def comments(self, request, slug=None):
    post = self.get_object()

    if request.method == "GET":
      qs = Comment.objects.filter(post=post).select_related("author")
      return Response(CommentSerializer(qs, many=True).data)

    if not request.user.is_authenticated:
      return Response({"detail": "Authentication is required"}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = CommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    comment = serializer.save(post=post, author=request.user)

    client = redis.from_url(get_redis_url())
    payload = {
      "event": "comment_created",
      "post_slug": post.slug,
      "comment_id": comment.id,
      "author_id": request.user.id,
    }
    client.publish(COMMENTS_CHANNEL, json.dumps(payload))

    logger.info("Comment created post_slug=%s user_id=%s", post.slug, request.user.id)
    return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)