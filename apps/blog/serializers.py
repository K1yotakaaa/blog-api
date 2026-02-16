from rest_framework import serializers

from apps.blog.models import Category, Comment, Post, Tag


class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = ("id", "name", "slug")


class TagSerializer(serializers.ModelSerializer):
  class Meta:
    model = Tag
    fields = ("id", "name", "slug")


class PostSerializer(serializers.ModelSerializer):
  author = serializers.StringRelatedField(read_only=True)
  tags = serializers.PrimaryKeyRelatedField(
    queryset=Tag.objects.all(),
    many=True,
    required=False,
    allow_empty=True,
  )

  class Meta:
    model = Post
    fields = (
      "id",
      "author",
      "title",
      "slug",
      "body",
      "category",
      "tags",
      "status",
      "created_at",
      "updated_at",
    )
    read_only_fields = ("created_at", "updated_at")

  def create(self, validated_data):
    tags = validated_data.pop("tags", [])
    post = Post.objects.create(**validated_data)
    if tags:
      post.tags.set(tags)
    return post

  def update(self, instance, validated_data):
    tags = validated_data.pop("tags", None)

    for attr, value in validated_data.items():
      setattr(instance, attr, value)
    instance.save()

    if tags is not None:
      instance.tags.set(tags)

    return instance


class CommentSerializer(serializers.ModelSerializer):
  author = serializers.StringRelatedField(read_only=True)

  class Meta:
    model = Comment
    fields = ("id", "post", "author", "body", "created_at")
    read_only_fields = ("post", "created_at")