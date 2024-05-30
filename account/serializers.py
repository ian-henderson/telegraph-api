from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
    ValidationError,
)


User = get_user_model()


class PasswordChangeSerializer(Serializer):
    password = CharField(required=True, write_only=True)
    token = CharField(required=True)

    def validate(self, data):
        password = data.get("password")

        if len(password) < 8:
            raise ValidationError(
                {"password": "Password must be at least 8 characters long."}
            )

        validate_password(password)

        return data


class PasswordResetSerializer(Serializer):
    email = EmailField(required=True)


class PasswordResetTokenVerificationSerializer(Serializer):
    token = CharField(required=True)


class UserSerializer(ModelSerializer):
    class Meta:
        extra_kwargs = {"password": {"write_only": True}}
        fields = (
            "id",
            "password",
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
        )
        model = User

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = self.Meta.model(**validated_data)

        if password is not None:
            user.set_password(password)

        user.save()

        return user
