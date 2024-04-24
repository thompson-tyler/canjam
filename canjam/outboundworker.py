from queue import Queue
from threading import Thread, Semaphore

from canjam.jamsocket import Jamsocket, address
from canjam.message import Message, Sound, Die
from canjam.logger import vprint


class OutboundWorker:
    """
    A multi-threaded worker that sends outgoing messages through a Jamsocket.
    The worker pulls messages from a queue and sends them to the specified
    address. Depending on the message type, the worker will either send the
    message reliably or unreliably. The worker can be started and stopped with
    the start() and stop() methods, or by using with...as syntax.
    """

    sock: Jamsocket
    out_queue: Queue[tuple[Message, address]]
    __worker_thread: Thread

    def __init__(
        self,
        sock: Jamsocket,
        notifier: Semaphore,
        name: str,
        out_queue: Queue[Message] = Queue(),
    ):
        self.sock = sock
        self.name = name

        self.out_queue = out_queue
        self.notifier = notifier

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
                    self.sock.sendto_unreliably(message.serialize(), address)
                case _:
                    vprint(f"Reliably sending {message}!")
                    self.sock.sendto_reliably(message.serialize(), address)
