import unittest
from queue import Queue

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
        worker = OutboundWorker(sock, out_queue)
        worker.start()
        worker.stop()
        sock.close()

    def test_with_block(self):
        out_queue = Queue()
        with Jamsocket(PORT1) as sock, OutboundWorker(sock, out_queue) as _:
            pass

    def test_with_defaults(self):
        with Jamsocket(PORT1) as sock, OutboundWorker(sock) as _:
            pass

    def test_sound_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((Sound(1), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, Sound)
            self.assertEqual(message.sound, 1)

    def test_req_user_list_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((ReqUserList(), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, ReqUserList)

    def test_rsp_user_list_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((RspUserList("name", []), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, RspUserList)
            self.assertEqual(message.source_name, "name")
            self.assertEqual(message.user_list, [])

    def test_new_user_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((NewUser("name"), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, NewUser)
            self.assertEqual(message.name, "name")

    def test_del_user_message(self):
        with Jamsocket(PORT1) as sock1, Jamsocket(PORT2) as sock2, OutboundWorker(
            sock2
        ) as worker:
            sock2.connect(LOCAL_ADDRESS)
            worker.out_queue.put((DelUser("name"), LOCAL_ADDRESS))
            data = sock1.recv()
            message = Message.deserialize(data)
            self.assertIsInstance(message, DelUser)
            self.assertEqual(message.name, "name")
