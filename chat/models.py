from django.contrib.auth import get_user_model
from django.db.models import (
    CASCADE,
    Count,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    Model,
    TextField,
)

from api.kms import kms_client

User = get_user_model()


class Room(Model):
    created_at = DateTimeField(auto_now_add=True)
    members = ManyToManyField(User, through="RoomMembership")

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Room(id={self.id})"

    @property
    def display_members(self):
        return ", ".join(member.username for member in self.members.all())

    display_members.fget.short_description = "Members"

    def get_room_by_usernames(usernames: list[str]) -> object or None:
        rooms = Room.objects.annotate(num_members=Count("members")).filter(
            num_members=len(usernames)
        )

        for username in usernames:
            rooms = rooms.filter(members__username=username)

        return rooms.first()


class RoomMembership(Model):
    date_joined = DateTimeField(auto_now_add=True)
    room = ForeignKey(Room, on_delete=CASCADE, related_name="memberships")
    user = ForeignKey(User, on_delete=CASCADE, related_name="memberships")

    def __str__(self):
        return f"RoomMembership(id={self.id}, room={self.room}, user='{self.user}')"

    @property
    def display_room_members(self):
        return ", ".join(member.username for member in self.room.members.all())

    display_room_members.fget.short_description = "Room Members"


class Message(Model):
    created_at = DateTimeField(auto_now_add=True)
    room = ForeignKey(Room, on_delete=CASCADE)
    sender = ForeignKey(User, on_delete=CASCADE)
    _content = TextField(db_column="content", default="")

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Message(id={self.id}, room={self.room.id}, sender='{self.sender.username}')"

    @property
    def content(self):
        return kms_client.decrypt(self._content)

    @content.setter
    def content(self, value):
        self._content = kms_client.encrypt(value)

    @property
    def display_room_members(self):
        return ", ".join(member.username for member in self.room.members.all())

    display_room_members.fget.short_description = "Room Members"

    def save(self, *args, **kwargs):
        if not self.pk:
            self._content = kms_client.encrypt(self._content)

        super(Message, self).save(*args, **kwargs)
