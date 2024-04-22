from queue import Queue
from time import time, sleep
from socket import gethostname, gethostbyname_ex
from argparse import Namespace

from canjam.jamsocket import Jamsocket, address
from canjam.inboundworker import InboundWorker
from canjam.outboundworker import OutboundWorker
from canjam.message import (
    Message,
    ReqUserList,
    RspUserList,
    NewUser,
    DelUser,
    Sound,
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

    def __init__(self, args: dict):
        """ """
        self.name = args.name
        self.join = args.join

        set_verbose(args.verbose)

        # If a port was not specified, default to 0 which will allow the OS to
        # auto-assign a port
        self.port: int = args.port or 0
        self.address = CanJammer.__get_my_addr__()

        self.in_queue: Queue[Message] = Queue()
        self.out_queue: Queue[tuple[Message, address]] = Queue()
        self.user_list = []

    def __bootstrap_connection__(self, sock: Jamsocket):
        """Set up CanJammer's user_list: if the user is joining another
        CanJam user's room, request the other user's user_list and send
        NewUser messages to each new peer. Then, print out the user's
        current hosting IP and port for other users to join this user.
        """

        if self.join:
            self.user_list = self.__request_user_list__(sock)

            # Send NewUser message out to all new connected peers
            new_user_message = NewUser(self.name)
            for user in self.user_list:
                self.out_queue.put((new_user_message, user.address))

        print("You're reachable at:")
        print(f"\t{self.address}:{sock.getsockname()[1]}")

        vprint("User list:", self.user_list)

    def __request_user_list__(self, sock: Jamsocket, timeout=5) -> list[User]:
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
            message, from_addr = sock.recvfrom(too_late - time())
            match Message.deserialize(message):
                case RspUserList(peer_name, user_list):
                    user_list.append(User(peer_name, from_addr))
                    return user_list
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
        On receiving [ FINISH ]
        """

        with Jamsocket(self.port) as sock:
            self.__bootstrap_connection__(sock)

            # Connect to each user
            for user in self.user_list:
                sock.connect(user.address)
                vprint("Connected to", user.address)

            with (
                InboundWorker(
                    sock, self.name, self.in_queue, self.user_list
                ) as inbound_worker,
                OutboundWorker(sock, self.out_queue) as outbound_worker,
            ):
                try:
                    while True:
                        sleep(1)
                        for user in self.user_list:
                            self.out_queue.put((Sound(1), user.address))
                except KeyboardInterrupt:
                    pass
                finally:
                    del_user = DelUser(self.name)
                    for user in self.user_list:
                        print("Sending", del_user, "to", user.address)
                        self.out_queue.put((del_user, user.address))
