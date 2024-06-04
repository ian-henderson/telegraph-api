from typing import Dict, List, Optional


class RoomManager:
    """
    RoomManager handles the creation, registration, and management of rooms
        and their users.

    Attributes:
        rooms (Dict[int, Dict[str, List[str]]]):
            A dictionary mapping room IDs to room information, including room
            name and list of users.
        users (Dict[str, List[int]]):
            A dictionary mapping usernames to the list of room IDs they are
            part of.
    """

    def __init__(self) -> None:
        self.rooms: Dict[int, Dict[str, List[str]]] = {}
        self.users: Dict[str, List[int]] = {}

    def create_name(self, room_id: int) -> str:
        return f"chat_room_{room_id}"

    def get_name(self, room_id: int) -> Optional[str]:
        room_state = self.rooms.get(room_id)
        return room_state.get("name") if room_state else None

    def get_user_room_names(self, username: str) -> list[str]:
        room_ids = self.users.get(username, [])
        return [
            self.rooms[room_id]["name"] for room_id in room_ids if room_id in self.rooms
        ]

    def register(self, room_id: int, usernames: list[str] = []) -> None:
        if room_id in self.rooms:
            self.rooms[room_id]["users"] = sorted(
                set(self.rooms[room_id].get("users", [])).union(usernames)
            )
        else:
            self.rooms[room_id] = {
                "name": self.create_name(room_id),
                "users": sorted(usernames),
            }

        for username in usernames:
            if room_id not in self.users.setdefault(username, []):
                self.users[username].append(room_id)

    def remove_user(self, username: str) -> None:
        room_ids = self.users.pop(username, [])

        for room_id in room_ids:
            if room_id in self.rooms:
                self.rooms[room_id]["users"] = [
                    user for user in self.rooms[room_id]["users"] if user != username
                ]

                if not self.rooms[room_id]["users"]:
                    del self.rooms[room_id]

    def user_is_in_room(self, username: str, room_id: int) -> bool:
        return room_id in self.rooms and username in self.rooms[room_id].get(
            "users", []
        )
