from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    CharField,
    IntegerField,
    ListSerializer,
    ModelSerializer,
    SerializerMethodField,
)

from account.serializers import UserSerializer
from .models import Message, Room, RoomMembership


User = get_user_model()


class MessageSerializer(ModelSerializer):
    _content = CharField(write_only=True)
    content = SerializerMethodField()
    sender = UserSerializer(read_only=True)
    sender_id = IntegerField(required=True, write_only=True)

    class Meta:
        fields = (
            "id",
            "created_at",
            "content",
            "room",
            "sender",
            "sender_id",
            "_content",
        )
        model = Message
        read_only_fields = ("content",)

    # This calls the content property getter on the Message model
    def get_content(self, message):
        return message.content


class RoomMembershipSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        fields = ("id", "date_joined", "room", "user")
        model = RoomMembership


class RoomSerializer(ModelSerializer):
    member_ids = ListSerializer(child=IntegerField(), required=True, write_only=True)

    class Meta:
        fields = ("id", "created_at", "member_ids", "memberships")
        model = Room
        read_only_fields = ("memberships",)

    def create(self, validated_data):
        member_ids = validated_data.pop("member_ids")

        try:
            with transaction.atomic():
                room = Room.objects.create(**validated_data)
                for member_id in member_ids:
                    RoomMembership.objects.create(room=room, user_id=member_id)

        except Exception as exception:
            raise ValidationError(exception)

        return room


class NestedRoomSerializer(ModelSerializer):
    memberships = RoomMembershipSerializer(many=True, read_only=True)

    class Meta:
        fields = ("id", "created_at", "memberships")
        model = Room
