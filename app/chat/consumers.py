import asyncio
import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError
from typing import List, Optional

from .models import Room
from .serializers import MessageSerializer, RoomSerializer
from .utils import RoomManager


User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    room_manager = RoomManager()

    async def connect(self) -> None:
        await self.accept()
        user = self.get_user()
        logging.info(f"Accepted websocket connection for {user}.")

        rooms_ids = await self.get_user_room_ids()
        for room_id in rooms_ids:
            self.room_manager.register(room_id, usernames=[user.username])

        # adds room groups
        tasks = [
            self.channel_layer.group_add(
                self.room_manager.get_name(room_id), self.channel_name
            )
            for room_id in rooms_ids
        ]

        # adds user group
        tasks.append(
            self.channel_layer.group_add(self.get_user_group_name(), self.channel_name),
        )

        try:
            await asyncio.gather(*tasks)
        except Exception as exception:
            error = "Failed to add groups"
            logging.error(f"{error}: {exception}")
            await self.send_error(error + ".")
            return await self.close()

        logging.info(f"Subscribed to groups for {user}.")

    @database_sync_to_async
    def create_message(self, message_data: object) -> (str, object):
        serializer = MessageSerializer(data=message_data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return str(message), serializer.data

    @database_sync_to_async
    def create_room(self, usernames: List[str]) -> Optional[Room]:
        users_query = User.objects.filter(username__in=usernames)
        member_ids = [user.id for user in users_query]
        serializer = RoomSerializer(data={"member_ids": member_ids})
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    async def disconnect(self, close_code) -> None:
        user = self.get_user()
        logging.info(f"Disconnected websocket connection for {user}.")

        # discards room groups
        tasks = [
            self.channel_layer.group_discard(name, self.channel_name)
            for name in self.room_manager.get_user_room_names(user.username)
        ]

        # discards user group
        tasks.append(
            self.channel_layer.group_discard(
                self.get_user_group_name(), self.channel_name
            )
        )

        try:
            await asyncio.gather(*tasks)
        except Exception as exception:
            return logging.error(f"Failed to discard groups for {user}: {exception}")

        self.room_manager.remove_user(user.username)
        logging.info(f"Discarded groups for {user}.")

    @database_sync_to_async
    def get_room(
        self, room_id: Optional[int], usernames: List[str] = []
    ) -> Optional[Room]:
        room = None
        if room_id is not None:
            room = Room.objects.filter(id=room_id).first()
        return room or Room.get_room_by_usernames(usernames)

    def get_user(self) -> User:
        return self.scope["user"]

    def get_user_group_name(self, username: Optional[str] = None) -> str:
        return f"chat_user_{username or self.get_user().username}"

    @database_sync_to_async
    def get_user_room_ids(self) -> list[int]:
        return [membership.room.id for membership in self.get_user().memberships.all()]

    async def handle_create_message(self, payload: object):
        message_data = payload.get("message")
        room_id = message_data.get("room_id")
        user = self.get_user()
        usernames = message_data.get("usernames", [])

        if user.username not in usernames:
            usernames.append(user.username)

        room = await self.get_room(room_id, usernames)

        if room and not await self.is_user_member_of_room(room):
            warning = "Logged-in user is not member of room."
            logging.warning(warning)
            return await self.send_warning(warning)

        new_room = False

        if not room:
            try:
                room = await self.create_room(usernames)
            except ValidationError as error:
                message = "Failed to create room"
                logging.error(f"{message}: {error}")
                return await self.send_error(message + ".")

            logging.info(f"Created {room}.")
            new_room = True

        message_data["room"] = room.id
        message_data["sender_id"] = user.id
        message_data["_content"] = message_data["content"]

        try:
            message_str, message = await self.create_message(message_data)
        except (Exception, ValidationError) as exception:
            error = "Failed to create message"
            logging.error(f"{error}: {exception}")
            return await self.send_error(error + ".")

        logging.info(f"Created {message_str}.")
        message_payload = {"type": "message.created", "message": message}
        tasks = []

        # Send new message to users' individual channels if the room is new.
        if new_room:
            for username in usernames:
                tasks.append(
                    self.channel_layer.group_send(
                        self.get_user_group_name(username), message_payload
                    )
                )
        # Otherwise, send new message to existing room group.
        else:
            tasks.append(
                self.channel_layer.group_send(
                    self.room_manager.get_name(room.id), message_payload
                )
            )

        try:
            await asyncio.gather(*tasks)
        except Exception as exception:
            error = "Failed to send message.created event to group(s)"
            logging.error(f"{error}: {exception}")
            return await self.send_error(error + ".")

        logging.info(f"Sent {message_str} to groups.")

    @database_sync_to_async
    def is_user_member_of_room(self, room: Room) -> bool:
        return self.get_user() in room.members.all()

    # magically called by parent class AsyncWebsocketConsumer via event.type
    async def message_created(self, event: dict) -> None:
        await self.send_event(event)

        message = event.get("message", {})
        room_id = message.get("room", None)
        user = self.get_user()

        # Early exit if user already associated with room
        if self.room_manager.user_is_in_room(user.username, room_id):
            return

        # Registers user with new room
        self.room_manager.register(room_id=room_id, usernames=[user.username])
        room_name = self.room_manager.get_name(room_id)
        try:
            await self.channel_layer.group_add(room_name, self.channel_name)
        except Exception as exception:
            error = f"Failed to add group '{room_name}' to {user}"
            logging.error(f"{error}: {exception}")
            return await self.send_error(error + ".")

        logging.info(f"Added new room group for {user}.")

    async def receive(self, text_data):
        message = json.loads(text_data)
        command_type = message.get("type")
        payload = message.get("payload")

        if command_type == "create.message":
            return await self.handle_create_message(payload)

        warning = f"{command_type} isn't a valid command."
        logging.warning(warning)
        await self.send_warning(warning)

    async def send_error(self, error: str) -> None:
        await self.send(text_data=json.dumps({"error": error}))

    async def send_event(self, event: dict) -> None:
        await self.send(text_data=json.dumps({"event": event}))

    async def send_message(self, message: str) -> None:
        await self.send(text_data=json.dumps({"message": message}))

    async def send_warning(self, warning: str) -> None:
        await self.send(text_data=json.dumps({"warning": warning}))
