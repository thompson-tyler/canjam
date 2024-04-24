from queue import Queue
from time import time
from socket import gethostname, gethostbyname_ex
from argparse import Namespace
from threading import Semaphore

from canjam.jamsocket import Jamsocket, address
from canjam.inboundworker import InboundWorker
from canjam.outboundworker import OutboundWorker
from canjam.message import (
    Message,
    ReqUserList,
    RspUserList,
    NewUser,
    DelUser,
)
from canjam.user import User
from canjam.logger import vprint, set_verbose


class CanJammer:
    """
    A multi-threaded manager that oversees communications between the
    InboundWorker, OutboundWorker, and GameRunner threads. The CanJammer
    initializes the shared server state (e.g. the list of connected Users)
    and the shared JamSocket, bootstrapping a connection with its first
    CanJam peer if specified.
    """

    def __init__(self, args: Namespace):
        """ """
        self.join = args.join

        set_verbose(args.verbose)

        # If a port was not specified, default to 0 which will allow the OS to
        # auto-assign a port
        self.name = args.name
        self.port: int = args.port or 0
        self.address = CanJammer.__get_my_addr__()

        self.in_queue = Queue()
        self.out_queue = Queue()
        self.user_set = set()

        self.notifier = Semaphore(0)

    def __bootstrap_connection__(self, sock: Jamsocket):
        """Set up CanJammer's user_set: if the user is joining another
        CanJam user's room, request the other user's user_set and send
        NewUser messages to each new peer. Then, print out the user's
        current hosting IP and port for other users to join this user.
        """

        if self.join:
            self.user_set = self.__request_user_set__(sock)

            # Send NewUser message out to all new connected peers
            new_user_message = NewUser(self.name)
            for user in self.user_set:
                self.out_queue.put((new_user_message, user.address))

        print("You're reachable at:")
        print(f"\t{self.address}:{sock.getsockname()[1]}")

    def __request_user_set__(self, sock: Jamsocket, timeout=5) -> list[User]:
        """
        Requests a room's user list from a peer at the specified address. A new
        socket connection will be made with the peer. If the peer does not
        respond with the user list with the specified timeout, a TimeoutError
        will be raised.
        """

        addr = CanJammer.__parse_address__(self.join)
        vprint(f"Joining peer room at {addr}")

        # Try to acquire the user list from the specified address
        try:
            sock.connect(addr)
            assert sock.sendto_reliably(ReqUserList().serialize(), addr)
        except:
            raise TimeoutError(f"Failed to reach peer at {addr}")

        # Wait for the proper response
        too_late = time() + timeout
        while time() < too_late:
            msg, from_addr = sock.recvfrom(too_late - time())
            match Message.deserialize(msg):
                case RspUserList(peer_name, user_set):
                    user_set.add(User(peer_name, from_addr))
                    return user_set
                case _:
                    pass

        raise TimeoutError("Failed to receive user list from peer")

    def __parse_address__(address: str) -> address:
        """
        From a string of the format HOST:PORT where PORT is a valid integer, returns
        a tuple of the host and port as a string and integer, respectively. If the
        string is not in the correct format, a ValueError will be raised.
        """

        parts = address.split(":")
        if len(parts) != 2:
            raise ValueError("Address must be in the format HOST:PORT")
        host, port_str = parts
        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"Invalid port: {port_str}")
        return host, port

    def __get_my_addr__():
        """
        Attempts to get your local IP address. If it fails, it will return None.
        """
        _, _, aliases = gethostbyname_ex(gethostname())
        return next(filter(lambda x: x != "127.0.0.1", aliases), None)

    def run(self):
        """Set up connection with other CanJam peers. If the user is joining
        another CanJam user's room, set up connections to all peers.
        NOTE: CanJammer should spawn and manage GameRunner, as all non-sound
        pack handling is done by InboundWorker and OutboundWorker. Can't
        remember: any state changes that _need_ to notify CanJammer to do
        work for another thread?
        """

        with Jamsocket(self.port) as sock:
            self.__bootstrap_connection__(sock)

            with (
                InboundWorker(
                    sock, self.notifier, self.name, self.in_queue, self.user_set
                ) as inbound_worker,
                OutboundWorker(
                    sock, self.notifier, self.name, self.out_queue
                ) as outbound_worker,
            ):
                try:
                    # TODO: start the GameRunner module

                    # TODO: change to checking some sort of internal flag indicating what CanJammer was awoken for
                    while True:
                        self.notifier.acquire()
                        vprint(f"User list is now {self.user_set}!")
                except KeyboardInterrupt:
                    pass
                finally:
                    # Notify all connected peers that CanJam user is leaving
                    del_user = DelUser(self.name)

                    for user in self.user_set:
                        print("Sending", del_user, "to", user.address)
                        self.out_queue.put((del_user, user.address))
