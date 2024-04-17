import unittest
from queue import Queue

from canjam.inboundworker import InboundWorker
from canjam.jamsocket import Jamsocket
from canjam.message import Message, Sound, ReqUserList, RspUserList
from canjam.user import User


PORT1 = 1024
PORT2 = 1025
LOCAL_ADDRESS = ("localhost", PORT1)


class InboundWorkerTestCase(unittest.TestCase):
    def test_start_stop(self):
        sock = Jamsocket(PORT1)
        in_queue = Queue()
        user_list = []
        worker = InboundWorker(sock, in_queue, user_list)
        worker.start()
        worker.stop()
        sock.close()

    def test_with_block(self):
        in_queue = Queue()
        user_list = []
        with Jamsocket(PORT1) as sock, InboundWorker(
            sock, in_queue, user_list
        ) as _:
            pass

    def test_with_defaults(self):
        with Jamsocket(PORT1) as sock, InboundWorker(sock) as _:
            pass

    def test_sound_message(self):
        with Jamsocket(PORT1) as sock, InboundWorker(sock) as worker:
            sound = Sound(1)
            sock.connect(LOCAL_ADDRESS)
            sock.sendto_reliably(sound.serialize(), LOCAL_ADDRESS)
            queue = worker.in_queue
            message = queue.get()
            self.assertIsInstance(message, Sound)
            self.assertEqual(message.sound, 1)

    def test_list_request(self):
        with Jamsocket(PORT1) as sock1, InboundWorker(
            sock1
        ) as worker, Jamsocket(PORT2) as sock2:
            worker.user_list.append(User("name", ("localhost", PORT2)))

            sock2.connect(LOCAL_ADDRESS)
            assert sock2.sendto_reliably(
                ReqUserList().serialize(), LOCAL_ADDRESS
            )

            rsp = sock2.recv()
            message = Message.deserialize(rsp)

            self.assertIsInstance(message, RspUserList)
            self.assertEqual(message.user_list, worker.user_list)
