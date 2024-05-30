from django.urls import path

from .views import MessageListView, RoomDetailView, RoomListView


urlpatterns = [
    path("room", RoomDetailView.as_view(), name="room-detail"),
    path("rooms", RoomListView.as_view(), name="room-list"),
    path("room/<int:room_id>/messages", MessageListView.as_view(), name="message-list"),
]
