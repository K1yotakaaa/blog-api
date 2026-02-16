from __future__ import annotations
from django.db import models

from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager["User"]):
  def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> "User":
    if not email:
      raise ValueError("Email is required")

    email = self.normalize_email(email).lower()
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)

    return user
  
  def create_superuser(self, email: str, password: str, **extra_fields: Any) -> "User":
    extra_fields.setdefault("is_staff", True)
    extra_fields.setdefault("is_superuser", True)
    extra_fields.setdefault("is_active", True)

    return self.create_user(email=email, password=password, **extra_fields)
  

class User(AbstractBaseUser, PermissionsMixin):
  email = models.EmailField(unique=True)
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)

  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)

  date_joined = models.DateTimeField(default=timezone.now)
  avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

  objects = UserManager()

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["first_name", "last_name"]

  def __str__(self) -> str:
    return self.email
