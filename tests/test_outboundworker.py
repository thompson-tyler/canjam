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
    Color,
)
from canjam.canjamsynth import SynthType
from canjam.user import User


class OutboundWorkerTestCase(unittest.TestCase):
    def test_start_stop(self):
        sock = Jamsocket(0)
        worker = OutboundWorker(sock, "Skylar", Queue(), set())
        worker.start()
        worker.stop()
        sock.close()

    def test_with_block(self):
        out_queue = Queue()
        with (
            Jamsocket(0) as sock,
            OutboundWorker(sock, "Skylar", out_queue, set()) as _,
        ):
            pass

    def test_with_defaults(self):
        with Jamsocket(0) as sock, OutboundWorker(sock, "Skylar") as _:
            pass

    def test_sound_message(self):
        with (
            Jamsocket(0) as sock1,
            Jamsocket(0) as sock2,
            OutboundWorker(sock2, "Skylar") as worker,
        ):
            sock2.connect(sock1.getsockname())
            worker.user_set.add(User("Skylar", sock1.getsockname()))
            worker.out_queue.put((Sound(1, Color.BLACK, SynthType.BELLS), None))
            data = sock1.recv(1)
            message = Message.deserialize(data)
            self.assertIsInstance(message, Sound)
            match message:
                case Sound(note, color, synth_type):
                    self.assertEqual(note, 1)
                    self.assertEqual(color, Color.BLACK)
                    self.assertEqual(synth_type, SynthType.BELLS)
                case _:
                    self.fail("Deserialized message is not of the correct type")

    def test_multi_sound_message(self):
        with (
            Jamsocket(0) as sock1,
            Jamsocket(0) as sock2,
            Jamsocket(0) as sock3,
            OutboundWorker(sock3, "Skylar") as worker,
        ):
            sock3.connect(sock1.getsockname())
            sock3.connect(sock2.getsockname())
            worker.user_set.add(User("Roger", sock1.getsockname()))
            worker.user_set.add(User("Cece", sock2.getsockname()))
            worker.out_queue.put((Sound(1, Color.BLACK, SynthType.BELLS), None))
            datas = [sock1.recv(1), sock2.recv(1)]
            messages = map(Message.deserialize, datas)
            [self.assertIsInstance(message, Sound) for message in messages]
            for message in messages:
                match message:
                    case Sound(note, color, synth_type):
                        self.assertEqual(note, 1)
                        self.assertEqual(color, Color.BLACK)
                        self.assertEqual(synth_type, SynthType.BELLS)
                    case _:
                        self.fail(
                            "Deserialized message is not of the correct type"
                        )

    def test_req_user_set_message(self):
        with (
            Jamsocket(0) as sock1,
            Jamsocket(0) as sock2,
            OutboundWorker(sock2, "Skylar") as worker,
        ):
            sock2.connect(sock1.getsockname())
            worker.out_queue.put((ReqUserList(), sock1.getsockname()))
            data = sock1.recv(1)
            message = Message.deserialize(data)
            self.assertIsInstance(message, ReqUserList)

    def test_rsp_user_set_message(self):
        with (
            Jamsocket(0) as sock1,
            Jamsocket(0) as sock2,
            OutboundWorker(sock2, "Skylar") as worker,
        ):
            sock2.connect(sock1.getsockname())
            worker.out_queue.put(
                (RspUserList("name", set()), sock1.getsockname())
            )
            data = sock1.recv(1)
            message = Message.deserialize(data)
            self.assertIsInstance(message, RspUserList)
            match message:
                case RspUserList(source_name, user_set):
                    self.assertEqual(source_name, "name")
                    self.assertIsInstance(user_set, set)
                case _:
                    self.fail("Deserialized message is not of the correct type")

    def test_new_user_message(self):
        with (
            Jamsocket(0) as sock1,
            Jamsocket(0) as sock2,
            OutboundWorker(sock2, "Skylar") as worker,
        ):
            sock2.connect(sock1.getsockname())
            worker.out_queue.put((NewUser("name"), sock1.getsockname()))
            data = sock1.recv(1)
            message = Message.deserialize(data)
            self.assertIsInstance(message, NewUser)
            match message:
                case NewUser(name):
                    self.assertEqual(name, "name")
                case _:
                    self.fail("Deserialized message is not of the correct type")

    def test_del_user_message(self):
        with (
            Jamsocket(0) as sock1,
            Jamsocket(0) as sock2,
            OutboundWorker(sock2, "Skylar") as worker,
        ):
            sock2.connect(sock1.getsockname())
            worker.out_queue.put((DelUser("name"), sock1.getsockname()))
            data = sock1.recv(1)
            message = Message.deserialize(data)
            self.assertIsInstance(message, DelUser)
            match message:
                case DelUser(name):
                    self.assertEqual(name, "name")
                case _:
                    self.fail("Deserialized message is not of the correct type")
