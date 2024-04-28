import unittest


from canjam.user import User


class UserSerializationTest(unittest.TestCase):
    def test_serialize_deserialize_users(self):
        """
        Tests serialization and deserialization of many users with increasing
        name length and address
        """

        users = [User(str(i) * i, ("0.0.0.0", i)) for i in range(50)]
        data = [u.serialize() for u in users]
        self.assertEqual([User.deserialize(d) for d in data], users)

    def test_bad_deserialize_users(self):
        """
        Tests deserialization of bad data
        """

        with self.assertRaises(Exception):
            User.deserialize(b"bad data")


if __name__ == "__main__":
    unittest.main()
