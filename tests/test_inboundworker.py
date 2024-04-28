import unittest
from queue import Queue

from canjam.inboundworker import InboundWorker
from canjam.jamsocket import Jamsocket
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


class InboundWorkerTestCase(unittest.TestCase):
    def test_start_stop(self):
        sock = Jamsocket(0)
        in_queue = Queue()
        user_set = set()
        worker = InboundWorker(sock, "name", in_queue, user_set)
        worker.start()
        worker.stop()
        sock.close()

    def test_with_block(self):
        in_queue = Queue()
        user_set = set()
        with (
            Jamsocket(0) as sock,
            InboundWorker(sock, "Skylar", in_queue, user_set) as _,
        ):
            pass

    def test_with_defaults(self):
        with Jamsocket(0) as sock, InboundWorker(sock, "Skylar") as _:
            pass

    def test_sound_message(self):
        """Assert that InboundWorker can receive and process a Sound."""
        with Jamsocket(0) as sock, InboundWorker(sock, "Skylar") as worker:
            sound = Sound(1, Color.BLACK, SynthType.BELLS)
            sock.connect(sock.getsockname())
            sock.sendto_reliably(sound.serialize(), sock.getsockname())
            queue = worker.in_queue
            message = queue.get()
            self.assertIsInstance(message, Sound)
            match message:
                # True by the previous assertion, but just to be safe
                case Sound(note, color, synth_type):
                    self.assertEqual(note, 1)
                    self.assertEqual(color, Color.BLACK)
                    self.assertEqual(synth_type, SynthType.BELLS)
                case _:
                    self.fail("Unexpected message type")

    def test_list_request(self):
        """Assert that InboundWorker can receive a ReqUserList and respond
        with a ResUserList.
        """
        with (
            Jamsocket(0) as sock1,
            InboundWorker(sock1, "Skylar") as worker,
            Jamsocket(0) as sock2,
        ):
            tyler = User("Tyler", ("localhost", 1024))
            skylar = User("Skylar", ("localhost", 1024))
            worker.user_set.add(tyler)
            worker.user_set.add(skylar)

            sock2.connect(sock1.getsockname())
            assert sock2.sendto_reliably(
                ReqUserList().serialize(), sock1.getsockname()
            )

            rsp = sock2.recv()
            message = Message.deserialize(rsp)

            self.assertIsInstance(message, RspUserList)
            match message:
                case RspUserList(source_name, user_set):
                    self.assertEqual(source_name, "Skylar")
                    self.assertEqual(user_set, worker.user_set)

    def test_new_user(self):
        """Assert that InboundWorker will update internal user_set on
        receiving a NewUser.
        """
        with (
            Jamsocket(0) as sock1,
            InboundWorker(sock1, "Skylar") as worker,
            Jamsocket(0) as sock2,
        ):
            self.assertEqual(set(), worker.user_set)

            tyler = User("Tyler", ("localhost", sock1.getsockname()[1]))
            worker.user_set.add(tyler)

            sock2.connect(sock1.getsockname())
            cece = User("Cece", ("127.0.0.1", sock2.getsockname()[1]))
            assert sock2.sendto_reliably(
                NewUser("Cece").serialize(), sock1.getsockname()
            )

            worker.stop()
            self.assertEqual(set([tyler, cece]), worker.user_set)

    def test_del_user(self):
        """Assert that InboundWorker will update internal user_set on
        receiving a DelUser.
        """
        with (
            Jamsocket(0) as sock1,
            InboundWorker(sock1, "Skylar") as worker,
            Jamsocket(0) as sock2,
        ):
            tyler = User("Tyler", ("localhost", sock1.getsockname()[1]))
            cece = User("Cece", ("127.0.0.1", sock2.getsockname()[1]))
            worker.user_set.update([tyler, cece])

            sock2.connect(sock1.getsockname())
            assert sock2.sendto_reliably(
                DelUser("Cece").serialize(), sock1.getsockname()
            )

            worker.stop()
            self.assertEqual(worker.user_set, set([tyler]))

    def test_bad_message(self):
        """Test that receiving a poorly formatted message does not crash the
        InboundWorker.
        """
        with Jamsocket(0) as sock, InboundWorker(sock, "Skylar") as worker:
            sock.connect(sock.getsockname())
            sock.sendto_reliably(b"bad message", sock.getsockname())
