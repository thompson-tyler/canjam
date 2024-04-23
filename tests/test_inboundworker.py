import unittest
from threading import Semaphore
from queue import Queue

from canjam.inboundworker import InboundWorker
from canjam.jamsocket import Jamsocket
from canjam.message import Message, Sound, ReqUserList, RspUserList, NewUser, DelUser
from canjam.user import User


PORT1 = 1024
PORT2 = 1025
LOCAL_ADDRESS = ("localhost", PORT1)


class InboundWorkerTestCase(unittest.TestCase):
    def test_start_stop(self):
        sock = Jamsocket(PORT1)
        in_queue = Queue()
        user_set = set()
        worker = InboundWorker(sock, in_queue, user_set)
        worker.start()
        worker.stop()
        sock.close()

    def test_with_block(self):
        in_queue = Queue()
        user_set = set()
        with Jamsocket(PORT1) as sock, InboundWorker(
            sock, Semaphore(0), "Skylar", in_queue, user_set
        ) as _:
            pass

    def test_with_defaults(self):
        with Jamsocket(PORT1) as sock, InboundWorker(sock, Semaphore(0), "Skylar") as _:
            pass

    def test_sound_message(self):
        """Assert that InboundWorker can receive and process a Sound."""
        with Jamsocket(PORT1) as sock, InboundWorker(
            sock, 
            Semaphore(0),
            "Skylar"
        ) as worker:
            sound = Sound(1)
            sock.connect(LOCAL_ADDRESS)
            sock.sendto_reliably(sound.serialize(), LOCAL_ADDRESS)
            queue = worker.in_queue
            message = queue.get()
            self.assertIsInstance(message, Sound)
            self.assertEqual(message.sound, 1)

    def test_list_request(self):
        """Assert that InboundWorker can receive a ReqUserList and respond
        with a ResUserList.
        """
        with Jamsocket(PORT1) as sock1, InboundWorker(
            sock1,
            Semaphore(0),
            "Skylar"
        ) as worker, Jamsocket(PORT2) as sock2:
            tyler = User("Tyler", ("localhost", PORT2))
            skylar = User("Skylar", ("localhost", PORT2))
            worker.user_set.add(tyler)
            worker.user_set.add(skylar)

            sock2.connect(LOCAL_ADDRESS)
            assert sock2.sendto_reliably(ReqUserList().serialize(), LOCAL_ADDRESS)

            rsp = sock2.recv()
            message = Message.deserialize(rsp)

            self.assertIsInstance(message, RspUserList)
            self.assertEqual(message.user_set, set([tyler, skylar]))

    def test_new_user(self):
        """Assert that InboundWorker will update internal user_set on
        receiving a NewUser.
        """
        with Jamsocket(PORT1) as sock1, InboundWorker(
            sock1,
            Semaphore(0),
            "Skylar"
        ) as worker, Jamsocket(PORT2) as sock2:
            self.assertEqual(set(), worker.user_set)

            tyler = User("Tyler", ("localhost", PORT2))
            worker.user_set.add(tyler)

            sock2.connect(LOCAL_ADDRESS)
            cece = User("Cece", ("127.0.0.1", PORT2))
            assert sock2.sendto_reliably(NewUser("Cece").serialize(), LOCAL_ADDRESS)
            
            worker.stop()
            self.assertEqual(set([tyler, cece]), worker.user_set)

    def test_del_user(self):
        """Assert that InboundWorker will update internal user_set on
        receiving a DelUser.
        """
        with Jamsocket(PORT1) as sock1, InboundWorker(
            sock1,
            Semaphore(0),
            "Skylar"
        ) as worker, Jamsocket(PORT2) as sock2:
            tyler = User("Tyler", ("localhost", PORT2))
            cece = User("Cece", ("127.0.0.1", PORT2))
            worker.user_set.update([tyler, cece])

            sock2.connect(LOCAL_ADDRESS)
            tyler = User("Tyler", ("localhost", PORT2))
            assert sock2.sendto_reliably(DelUser("Cece").serialize(), LOCAL_ADDRESS)

            worker.stop()
            self.assertEqual(worker.user_set, set([tyler]))
