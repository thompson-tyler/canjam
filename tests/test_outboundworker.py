import unittest
from queue import Queue
from threading import Semaphore

from canjam.outboundworker import OutboundWorker
from canjam.jamsocket import Jamsocket
from canjam.message import (
    Message,
    Sound,
    ReqUserList,
    RspUserList,
    NewUser,
    DelUser,
)


PORT1 = 1024
PORT2 = 1025
LOCAL_ADDRESS = ("localhost", PORT1)


class OutboundWorkerTestCase(unittest.TestCase):
    def test_start_stop(self):
        sock = Jamsocket(PORT1)
        out_queue = Queue()
        worker = OutboundWorker(sock, Semaphore(0), "Skylar", out_queue)
        worker.start()
        worker.stop()
        sock.close()

    def test_with_block(self):
        out_queue = Queue()
        with Jamsocket(PORT1) as sock, OutboundWorker(sock, Semaphore(0), "Skylar", out_queue) as _:
            pass

    def test_with_defaults(self):
        with Jamsocket(PORT1) as sock, OutboundWorker(sock, Semaphore(0), "Skylar") as _:
            pass

    def test_sound_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2,
            Semaphore(0),
            "Skylar"
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((Sound(1), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, Sound)
            self.assertEqual(message.sound, 1)

    def test_req_user_set_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2,
            Semaphore(0),
            "Skylar"
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((ReqUserList(), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, ReqUserList)

    def test_rsp_user_set_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2,
            Semaphore(0),
            "Skylar"
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((RspUserList("name", set()), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, RspUserList)
            self.assertEqual(message.source_name, "name")
            self.assertEqual(message.user_set, set())

    def test_new_user_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2,
            Semaphore(0),
            "Skylar"
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((NewUser("name"), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, NewUser)
            self.assertEqual(message.name, "name")

    def test_del_user_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2,
            Semaphore(0),
            "Skylar"
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((DelUser("name"), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, DelUser)
            self.assertEqual(message.name, "name")
