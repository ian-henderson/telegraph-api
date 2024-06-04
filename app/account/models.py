from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager as DjangoUserManager,
)
from django.db.models import BooleanField, CharField, DateTimeField, EmailField, Model


class PasswordReset(Model):
    created_at = DateTimeField(auto_now_add=True)
    email = EmailField()
    token = CharField(max_length=100)

    def __str__(self):
        return f"PasswordReset(id={self.id}, email='{self.email}')"


class UserManager(DjangoUserManager):
    def _create_user(self, email, password, username, **extra_fields):
        if not email:
            raise ValueError("You haven't provided an email")

        if not username:
            raise ValueError("You haven't provided a username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, password=None, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, username, **extra_fields)

    def create_superuser(
        self, email=None, password=None, username=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self._create_user(email, password, username, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)

    objects = UserManager()

    email = EmailField(blank=True, default="", unique=True)
    first_name = CharField(blank=True, default="", max_length=255)
    last_name = CharField(blank=True, default="", max_length=255)
    username = CharField(default="", max_length=50, unique=True)

    date_joined = DateTimeField(auto_now_add=True)
    last_login = DateTimeField(blank=True, null=True)

    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    class Meta:
        ordering = ("last_name", "first_name", "username")
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"User(id={self.id}, username='{self.username}')"

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"

        return self.first_name or self.last_name or ""
