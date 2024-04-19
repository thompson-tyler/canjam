from argparse import ArgumentParser
from queue import Queue
from time import time, sleep
from socket import gethostname, gethostbyname_ex

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


def build_parser():
    """
    Builds and returns an ArgumentParser object that can be used to parse
    command line arguments for the Canjam program.
    """

    parser = ArgumentParser()
    parser.add_argument(
        "--name",
        "-n",
        type=str,
        required=True,
        help="The name to use when joining a room.",
    )
    parser.add_argument(
        "--join",
        "-j",
        type=str,
        metavar="HOST:PORT",
        help="Join a room by specifying the address of someone in the room. "
        + "If not specified, a new empty room will be created.",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        help="The port to use for internet communication. If not specified,"
        + "then the OS will assign you one.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print more information to the console.",
    )
    return parser


def parse_address(address: str) -> address:
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


def request_user_list(addr: address, sock: Jamsocket, timeout=5):
    """
    Requests a room's user list from a peer at the specified address. A new
    socket connection will be made with the peer. If the peer does not respond
    with the user list with the specified timeout, a TimeoutError will be
    raised
    """

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


def get_my_addr():
    """
    Attempts to get your local IP address. If it fails, it will return None.
    """
    # gethostnameby_ex sometimes failes with an exception
    try:
        _, _, aliases = gethostbyname_ex(gethostname())
        return next(filter(lambda x: x != "127.0.0.1", aliases), None)
    except:
        return None


def main():
    parser = build_parser()
    args = parser.parse_args()

    set_verbose(args.verbose)

    my_name: str = args.name
    # If a port was not specified, default to 0 which will allow the OS to
    # auto-assign a port
    port: int = args.port or 0
    my_addr = get_my_addr()
    user_list: list[User] = []
    in_queue: Queue[Message] = Queue()
    out_queue: Queue[tuple[Message, address]] = Queue()
    with Jamsocket(port) as sock:
        # If a join address was specified, get the user list from that address
        if args.join:
            peer_addr = parse_address(args.join)
            vprint(f"Joining room from peer at {peer_addr}")
            user_list = request_user_list(peer_addr, sock)
            new_user_message = NewUser(my_name)
            for user in user_list:
                out_queue.put((new_user_message, user.address))

        vprint("Acquired user list:", user_list)

        for user in user_list:
            sock.connect(user.address)
            vprint("Connected to", user.address)

        print("You're reachable at:")
        print(f"\t{my_addr}:{sock.getsockname()[1]}")

        with (
            InboundWorker(sock, my_name, in_queue, user_list) as inbound_worker,
            OutboundWorker(sock, out_queue) as outbound_worker,
        ):
            try:
                while True:
                    sleep(1)
                    for user in user_list:
                        out_queue.put((Sound(1), user.address))
            except KeyboardInterrupt:
                pass
            finally:
                del_user_message = DelUser(my_name)
                for user in user_list:
                    print("Sending", del_user_message, "to", user.address)
                    out_queue.put((del_user_message, user.address))


if __name__ == "__main__":
    main()
