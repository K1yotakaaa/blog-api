from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ("id", "email", "first_name", "last_name", "avatar", "date_joined")


class RegisterSerializer(serializers.Serializer):
  email = serializers.EmailField()
  first_name = serializers.CharField(max_length=50)
  last_name = serializers.CharField(max_length=50)
  password = serializers.CharField(write_only=True)
  password2 = serializers.CharField(write_only=True)

  def validate(self, attrs):
    if attrs["password"] != attrs["password2"]:
      raise serializers.ValidationError({"password": "Passwords dont match"})
    return attrs
  
  def create(self, validated_data):
    validated_data.pop("password2")
    password = validated_data.pop("password")
    user = User.objects.create_user(password=password, **validated_data)
    return user