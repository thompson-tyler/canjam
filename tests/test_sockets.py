from pickle import dumps, loads
from socket import AF_INET, SOCK_DGRAM
import unittest
from threading import Thread

from canjam.badsocket import badsocket
from canjam.jamsocket import Jamsocket
from canjam.message import Message, RspUserList
from canjam.user import User


LOCALHOST = "127.0.0.1"
PORT1 = 1024
PORT2 = 1025


class CustomSocketTest(unittest.TestCase):
    """A test case for the badsocket and jamsocket classes"""

    def test_badsocket_init(self):
        with badsocket(AF_INET, SOCK_DGRAM) as sock:
            sock.bind((LOCALHOST, PORT1))
            self.assertIsInstance(sock, badsocket)

    def test_badsocket_sendto_return_value(self):
        """Make sure badsocket.sendto returns the length of the data sent."""
        with (
            badsocket(AF_INET, SOCK_DGRAM) as sock1,
            badsocket(AF_INET, SOCK_DGRAM) as sock2,
        ):
            sock1.bind((LOCALHOST, PORT1))
            data = b"Hello, World!"
            length = sock2.sendto(data, (LOCALHOST, PORT1))
            self.assertEqual(length, len(data))

    def test_jamsocket_init(self):
        """Initialize a jamsocket with default socket"""
        with Jamsocket(PORT1) as sock:
            self.assertIsInstance(sock, Jamsocket)

    def test_jamsocket_init_badsocket(self):
        """Initialize a jacksocket with a badsocket to make sure it doesn't crash"""
        with Jamsocket(PORT1, badsocket) as sock:
            self.assertIsInstance(sock, Jamsocket)

    def test_jamsocket_regular_socket(self):
        """
        Test jamsocket with default (regular) socket, which should work reliably because we're sending packets to ourselves
        As a bonus, this tests the unreliable sendto method
        """
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2:
            sock2.connect((LOCALHOST, PORT1))
            data = b"Hello, World!"
            size = sock2.sendto_unreliably(data, (LOCALHOST, PORT1))
            self.assertEqual(size, len(data))
            data = sock1.recv()
            self.assertEqual(data, b"Hello, World!")

    def test_jamsocket_bad_socket(self):
        """
        Test jamsocket with badsocket, which should work but with some packets lost
        """
        with (
            Jamsocket(PORT1, badsocket) as sock1,
            Jamsocket(PORT2, badsocket) as sock2,
        ):
            sock2.connect((LOCALHOST, PORT1))
            data = b"Hello, World!"
            size = sock2.sendto_reliably(data, (LOCALHOST, PORT1))
            self.assertEqual(size, len(data))
            data = sock1.recv()
            self.assertEqual(data, b"Hello, World!")

    def test_jamsocket_many_messages(self):
        """
        Test that sending many packets over a jamsocket with an unreliable
        underlying socket works.
        """
        with (
            Jamsocket(PORT1, badsocket) as sock1,
            Jamsocket(PORT2, badsocket) as sock2,
        ):
            for i in range(50):
                sock1.connect((LOCALHOST, PORT2))
                data = f"Hello, World! {i}".encode()
                size = sock2.sendto_reliably(data, (LOCALHOST, PORT1))
                self.assertEqual(size, len(data))
                rec_data = sock1.recv()
                self.assertEqual(data, rec_data)

    def test_jamsocket_bad_destination(self):
        """
        Test that sending a packet to a bad destination address raises an
        exception.
        """
        with Jamsocket(PORT1) as sock:
            with self.assertRaises(OSError):
                sock.sendto_unreliably(b"Hello, World!", ("1.2.3.4", PORT1))
            with self.assertRaises(OSError):
                sock.sendto_reliably(b"Hello, World!", ("1.2.3.4", PORT1))

    def test_jamsocket_not_listening(self):
        """
        Test that sending a packet to a host that isn't listening returns 0
        """
        with Jamsocket(PORT1) as sock1:
            sock2 = Jamsocket(PORT2)
            sock1.connect((LOCALHOST, PORT2))
            sock2.close()
            length = sock1.sendto_reliably(b"Hello, World!", (LOCALHOST, PORT2))
            self.assertEqual(length, 0)

    def test_jamsocket_thread_safety(self):
        """
        Tests sending many packets over a jamsocket from many threads.
        """

        I_RANGE = 20

        def send_job(sock, i):
            data = f"Hello, World! {i}".encode()
            size = sock.sendto_reliably(data, (LOCALHOST, PORT1))
            self.assertEqual(size, len(data))

        with (
            Jamsocket(PORT1, badsocket) as dest_sock,
            Jamsocket(PORT2, badsocket) as sock,
        ):
            sock.connect((LOCALHOST, PORT1))
            threads = []
            for i in range(I_RANGE):
                thread = Thread(target=send_job, args=(sock, i))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            received = set()
            for i in range(I_RANGE):
                data = dest_sock.recv()
                self.assertNotIn(data, received)
                received.add(data)

    def test_multiple_connects(self):
        """
        Tests that multiple peers connecting to one jamsocket work.
        """

        def connect_job(sock):
            sock.connect((LOCALHOST, PORT1))
            sock.close()

        with Jamsocket(PORT1, badsocket) as sock:
            socks = [Jamsocket(PORT2 + i, badsocket) for i in range(20)]

            threads = []
            for s in socks:
                thread = Thread(target=connect_job, args=(s,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

    def test_jamsocket_stress(self):
        """
        Tests sending many binary packets to a jamsocket from many threads.
        """

        I_RANGE = 20
        J_RANGE = 30

        # Sends 10 packets to the destination socket
        def send_job(sock, i):
            sock.connect((LOCALHOST, PORT1))
            for j in range(J_RANGE):
                data = dumps((i, j))
                size = sock.sendto_reliably(data, (LOCALHOST, PORT1))
                self.assertEqual(size, len(data))

        with Jamsocket(PORT1, badsocket) as dest_sock:
            threads = []
            sockets = []
            for i in range(I_RANGE):
                sock = Jamsocket(PORT2 + i, badsocket)
                thread = Thread(target=send_job, args=(sock, i))
                thread.start()
                threads.append(thread)
                sockets.append(sock)

            for thread in threads:
                thread.join()

            received = set()
            for i in range(I_RANGE * J_RANGE):
                data = dest_sock.recv()
                (i, j) = loads(data)
                received.add((i, j))

            for i in range(I_RANGE):
                for j in range(J_RANGE):
                    self.assertIn((i, j), received)

            for sock in sockets:
                sock.close()

    def test_sending_messages(self):
        """
        Tests sending serialized message objects over a jamsocket
        """

        with (
            Jamsocket(PORT1, badsocket) as dest_sock,
            Jamsocket(PORT2, badsocket) as sock,
        ):
            m = RspUserList([User("Alice", 1), User("Bob", 2)])
            data = m.serialize()

            sock.connect((LOCALHOST, PORT1))
            size = sock.sendto_reliably(data, (LOCALHOST, PORT1))
            self.assertEqual(size, len(data))
            rec_data = dest_sock.recv()
            rec_m = Message.deserialize(rec_data)
            match rec_m:
                case RspUserList(user_list):
                    self.assertIsInstance(user_list, list)
                    self.assertEqual(len(user_list), 2)
                    self.assertIsInstance(user_list[0], User)
                    self.assertIsInstance(user_list[1], User)
                    self.assertEqual(user_list[0].name, "Alice")
                    self.assertEqual(user_list[0].address, 1)
                    self.assertEqual(user_list[1].name, "Bob")
                    self.assertEqual(user_list[1].address, 2)
                case _:
                    self.fail("Deserialized message is not of the correct type")


if __name__ == "__main__":
    unittest.main()
