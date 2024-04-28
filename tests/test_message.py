from pickle import dumps
import unittest

from canjam.message import (
    Message,
    Sound,
    ReqUserList,
    RspUserList,
    NewUser,
    DelUser,
    Color,
)
from canjam.user import User
from canjam.gamerunner import SynthType


class MessageSerializationTest(unittest.TestCase):
    def test_serialize_sound_message(self):
        m = Sound(
            1,
            Color.BLACK,
            SynthType.BELLS,
        )
        data = m.serialize()
        m2 = Message.deserialize(data)
        match m2:
            case Sound(sound):
                self.assertEqual(sound, 1)
            case _:
                self.fail("Deserialized message is not of the correct type")

    def test_serialize_req_user_list_message(self):
        m = ReqUserList()
        data = m.serialize()
        m2 = Message.deserialize(data)
        self.assertIsInstance(m2, ReqUserList)

    def test_serialize_rsp_user_list_message(self):
        user_set = set()
        tyler = User("Tyler", ("localhost", 100))
        skylar = User("Skylar", ("localhost", 100))
        user_set.add(tyler)
        user_set.add(skylar)
        m = RspUserList("Eve", user_set)
        data = m.serialize()
        m2 = Message.deserialize(data)
        match m2:
            case RspUserList(name, user_set):
                self.assertIsInstance(name, str)
                self.assertEqual(name, "Eve")

                self.assertIsInstance(user_set, set)
                self.assertEqual(len(user_set), 2)
                for user in user_set:
                    self.assertIsInstance(user, User)
                    self.assertTrue(user in user_set)
            case _:
                self.fail("Deserialized message is not of the correct type")

    def test_serialize_new_user_message(self):
        m = NewUser("Alice")
        data = m.serialize()
        m2 = Message.deserialize(data)
        match m2:
            case NewUser(name):
                self.assertIsInstance(name, str)
                self.assertEqual(name, "Alice")
            case _:
                self.fail("Deserialized message is not of the correct type")

    def test_serialize_del_user_message(self):
        m = DelUser("Alice")
        data = m.serialize()
        m2 = Message.deserialize(data)
        match m2:
            case DelUser(name):
                self.assertIsInstance(name, str)
                self.assertEqual(name, "Alice")
            case _:
                self.fail("Deserialized message is not of the correct type")

    def test_bad_deserialize_message(self):
        """
        Tests deserialization of bad data
        """

        with self.assertRaises(Exception):
            Message.deserialize(b"bad data")

    def test_deserialize_other_object(self):
        """
        Tests deserialization of an object that is not a Message and ensure
        that an exception is raised
        """

        data = dumps("not a message")
        with self.assertRaises(Exception):
            Message.deserialize(data)


if __name__ == "__main__":
    unittest.main()
