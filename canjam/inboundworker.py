from queue import Queue
from threading import Thread

from canjam.jamsocket import Jamsocket
from canjam.message import (
    Message,
    Sound,
    ReqUserList,
    RspUserList,
    NewUser,
    DelUser,
    Die,
)
from canjam.user import User


class InboundWorker:
    """
    A multi-threaded worker that listens for incoming messages on a Jamsocket and
    processes them. The worker maintains a list of users and a queue of incoming
    Sound messages. The worker can be started and stopped with the start() and
    stop() methods, or by using with...as syntax.
    """

    sock: Jamsocket
    in_queue: Queue[Message]
    user_list: list[User]
    __worker_thread: Thread

    def __init__(
        self,
        sock: Jamsocket,
        in_queue: Queue[Message] = Queue(),
        user_list: list[User] = [],
    ):
        self.sock = sock
        self.in_queue = in_queue
        self.user_list = user_list
        self.__worker_thread = Thread(target=self.__worker_job)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def __worker_job(self):
        while True:
            data, address = self.sock.recvfrom()
            try:
                message = Message.deserialize(data)
            except:
                print("Failed to deserialize message from", address)
                continue
            match message:
                case ReqUserList():
                    rsp = RspUserList(self.user_list)
                    # TODO: handle this error case... remove user if they don't respond to the message?
                    assert self.sock.sendto_reliably(rsp.serialize(), address)
                case RspUserList(user_list):
                    existing = set(self.user_list)
                    new = set(user_list)
                    self.user_list.extend(new - existing)
                case NewUser(user):
                    self.user_list.append(user)
                case DelUser(user):
                    self.user_list.remove(user)
                case Sound(sound):
                    self.in_queue.put(message)
                case Die():
                    break
                case _:
                    print("Received unknown message type from", address)

    def start(self):
        self.__worker_thread.start()

    def stop(self):
        if self.__worker_thread.is_alive():
            self.sock.sendto_self(Die().serialize())
            self.__worker_thread.join()
