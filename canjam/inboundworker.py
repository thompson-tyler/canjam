from queue import Queue
from threading import Thread, Semaphore

from canjam.user import User
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
from canjam.logger import vprint


class InboundWorker:
    """
    A multi-threaded worker that listens for incoming messages on a Jamsocket and
    processes them. The worker maintains a list of users and a queue of incoming
    Sound messages. The worker can be started and stopped with the start() and
    stop() methods, or by using with...as syntax.
    """

    def __init__(
        self,
        sock: Jamsocket,
        notifier: Semaphore,
        name: str,
        in_queue: Queue[Message] = Queue(),
        user_set: set[User] = None
    ):
        self.sock = sock
        self.name = name

        self.in_queue = in_queue
        self.user_set = user_set if user_set else set()
        self.notifier = notifier

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
                    vprint("Received user list request from", address)
                    rsp = RspUserList(self.name, self.user_set)
                    # TODO: handle this error case... remove user if they don't respond to the message?
                    assert self.sock.sendto_reliably(rsp.serialize(), address)

                case RspUserList(peer_name, new_user_set):
                    vprint("Received user list response from", address)
                    new_user_set.add(User(peer_name, address))
                    self.user_set.update(new_user_set)
                    self.notifier.release()

                case NewUser(name):
                    vprint("New user", name, "from", address)
                    self.user_set.add(User(name, address))
                    self.notifier.release()

                case DelUser(name):
                    vprint("User", name, "left the room")
                    self.user_set.remove(User(name, address))
                    self.notifier.release()

                case Sound(sound):
                    vprint("Received sound", sound, "from", address)
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
