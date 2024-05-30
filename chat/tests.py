from django.test import TestCase

from .utils import RoomManager


class TestRoomManager(TestCase):
    def setUp(self):
        self.manager = RoomManager()

    def test_create_name(self):
        self.manager.__init__()
        self.assertEqual(self.manager.create_name(1), "chat_room_1")
        self.assertEqual(self.manager.create_name(2), "chat_room_2")

    def test_get_name(self):
        self.manager.__init__()
        self.manager.register(1)
        self.assertEqual(self.manager.get_name(1), "chat_room_1")
        self.assertIsNone(self.manager.get_name(2))

    def test_get_user_room_names(self):
        self.manager.__init__()
        self.manager.register(1, ["user1"])
        self.manager.register(2, ["user1", "user2"])
        self.assertEqual(
            self.manager.get_user_room_names("user1"), ["chat_room_1", "chat_room_2"]
        )
        self.assertEqual(self.manager.get_user_room_names("user2"), ["chat_room_2"])
        self.assertEqual(self.manager.get_user_room_names("user3"), [])

    def test_register(self):
        self.manager.__init__()
        self.manager.register(1, ["user1", "user2"])
        self.assertIn(1, self.manager.rooms)
        self.assertEqual(self.manager.rooms[1]["users"], ["user1", "user2"])
        self.assertIn("user1", self.manager.users)
        self.assertIn("user2", self.manager.users)
        self.assertEqual(self.manager.users["user1"], [1])
        self.assertEqual(self.manager.users["user2"], [1])

        # Register same room with more users
        self.manager.register(1, ["user3"])
        self.assertEqual(
            self.manager.rooms[1]["users"],
            ["user1", "user2", "user3"],
        )
        self.assertIn("user3", self.manager.users)
        self.assertEqual(self.manager.users["user3"], [1])

    def test_remove_user(self):
        self.manager.__init__()
        self.manager.register(1, ["user1", "user2"])
        self.manager.register(2, ["user1", "user3"])
        self.manager.remove_user("user1")
        self.assertNotIn("user1", self.manager.users)
        self.assertEqual(self.manager.rooms[1]["users"], ["user2"])
        self.assertEqual(self.manager.rooms[2]["users"], ["user3"])

        # Ensure room is deleted if it becomes empty
        self.manager.remove_user("user2")
        self.assertNotIn(1, self.manager.rooms)

        self.manager.remove_user("user3")
        self.assertNotIn(2, self.manager.rooms)

    def test_user_is_in_room(self):
        self.manager.__init__()
        self.manager.register(1, ["user1"])
        self.assertTrue(self.manager.user_is_in_room("user1", 1))
        self.assertFalse(self.manager.user_is_in_room("user1", 2))
        self.assertFalse(self.manager.user_is_in_room("user2", 1))
