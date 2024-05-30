import logging

from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from .models import Message, Room
from .serializers import MessageSerializer, NestedRoomSerializer


User = get_user_model()


class MessageListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer

    def get(self, request, room_id, *args, **kwargs):
        room = Room.objects.filter(id=room_id).first()

        if room is None:
            warning = f"Room '{room_id}' does not exist."
            logging.warning(warning)
            return Response({"warning": warning}, status=HTTP_400_BAD_REQUEST)

        if request.user not in room.members.all():
            warning = f"Logged-in user '{request.user}' is not a memeber of this room."
            logging.warning(warning)
            return Response({"warning": warning}, status=HTTP_401_UNAUTHORIZED)

        self.queryset = Message.objects.filter(room_id=room.id)

        return self.list(request, *args, **kwargs)


class RoomDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, format=None) -> Response:
        room_id = request.query_params.get("room")
        usernames = request.query_params.getlist("username", [])

        if request.user.username not in usernames:
            usernames.append(request.user.username)
            logging.info(
                f"Automatically included '{request.user.username}' in usernames list."
            )

        room = None

        # look up room by id
        if room_id:
            room = Room.objects.filter(id=room_id).first()
            if room:
                logging.info(f"Found room with room_id='{room_id}' lookup.")

        # look up room by usernames
        if not room:
            room = Room.get_room_by_usernames(usernames)
            if room:
                logging.info(f"Found room with usernames: {usernames}.")

        if not room:
            logging.info(f"Could not find room via {room_id=}, {usernames=}.")
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(NestedRoomSerializer(room).data)


class RoomListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = NestedRoomSerializer

    def get_queryset(self):
        return Room.objects.filter(members=self.request.user)
