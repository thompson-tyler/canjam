from queue import Queue
from threading import Thread, Semaphore

from canjam.jamsocket import Jamsocket, address
from canjam.message import Message, Sound, Die
from canjam.user import User
from canjam.logger import vprint


type OutQueueType = Queue[tuple[Message, address | None]]


class OutboundWorker:
    """
    A multi-threaded worker that sends outgoing messages through a Jamsocket.
    The worker pulls messages from a queue and sends them to the specified
    address. Depending on the message type, the worker will either send the
    message reliably or unreliably. The worker can be started and stopped with
    the start() and stop() methods, or by using with...as syntax.
    """

    sock: Jamsocket
    out_queue: OutQueueType
    __worker_thread: Thread

    def __init__(
        self,
        sock: Jamsocket,
        name: str,
        out_queue: OutQueueType | None = None,
        user_set: set[User] | None = None,
    ):
        self.sock = sock
        self.name = name
        self.user_set = user_set if user_set is not None else set()
        self.out_queue = out_queue if out_queue is not None else Queue()

        self.__worker_thread = Thread(target=self.__worker_job)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def start(self):
        self.__worker_thread.start()

    def stop(self):
        self.out_queue.put((Die(), None))
        self.__worker_thread.join()

    def __worker_job(self):
        while True:
            message, address = self.out_queue.get()
            match message:
                case Die():
                    return
                case Sound(_):
                    for user in self.user_set:
                        vprint(
                            f"Sending sound to {user.name} at {user.address}"
                        )
                        self.sock.sendto_unreliably(
                            message.serialize(), user.address
                        )
                case _:
                    vprint(f"Reliably sending {message}!")
                    if address is not None:
                        self.sock.sendto_reliably(message.serialize(), address)
