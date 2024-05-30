from django.contrib.admin import ModelAdmin, register, StackedInline

from .models import Message, Room, RoomMembership


@register(Message)
class MessageAdmin(ModelAdmin):
    fields = (
        "id",
        "sender",
        "room",
        "content",
        "created_at",
        "display_room_members",
    )
    list_display = (
        "id",
        "sender",
        "content",
        "room",
        "display_room_members",
    )
    readonly_fields = (
        "content",
        "created_at",
        "display_room_members",
        "id",
        "room",
        "sender",
    )


class MemberInline(StackedInline):
    extra = 0
    model = Room.members.through


@register(Room)
class RoomAdmin(ModelAdmin):
    inlines = (MemberInline,)
    list_display = ("id", "display_members", "created_at")
    readonly_fields = ("id", "created_at")


@register(RoomMembership)
class RoomMembershipAdmin(ModelAdmin):
    list_display = ("id", "room", "user", "display_room_members", "date_joined")
