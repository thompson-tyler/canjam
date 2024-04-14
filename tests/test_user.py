import unittest


from canjam.user import User


class UserSerializationTest(unittest.TestCase):
    def test_serialize_deserialize_users(self):
        """
        Tests serialization and deserialization of many users with increasing
        name length and address
        """

        users = [User(str(i) * i, i) for i in range(50)]
        data = [u.serialize() for u in users]
        for i in range(50):
            u = User.deserialize(data[i])
            self.assertEqual(u.name, str(i) * i)
            self.assertEqual(u.address, i)

    def test_bad_deserialize_users(self):
        """
        Tests deserialization of bad data
        """

        with self.assertRaises(Exception):
            User.deserialize(b"bad data")


if __name__ == "__main__":
    unittest.main()
