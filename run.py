from argparse import ArgumentParser
from queue import Queue
from time import time, sleep
from socket import gethostname, gethostbyname_ex

from canjam.canjammer import CanJammer


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


def main():
    parser = build_parser()
    args = parser.parse_args()

    canjammer: CanJammer = CanJammer(args)
    canjammer.run()

    # If a port was not specified, default to 0 which will allow the OS to
    # auto-assign a port
    # port: int = args.port or 0
    # my_addr = get_my_addr()
    # user_list: list[User] = []

    # in_queue: Queue[Message] = Queue()
    # out_queue: Queue[tuple[Message, address]] = Queue()

    # with Jamsocket(port) as sock:
    #     # If a join address was specified, get the user list from that address
    #     if args.join:
    #         peer_addr = parse_address(args.join)
    #         vprint(f"Joining room from peer at {peer_addr}")
    #         user_list = request_user_list(peer_addr, sock)
    #         new_user_message = NewUser(my_name)
    #         for user in user_list:
    #             out_queue.put((new_user_message, user.address))

    #     vprint("Acquired user list:", user_list)

    #     for user in user_list:
    #         sock.connect(user.address)
    #         vprint("Connected to", user.address)

    #     print("You're reachable at:")
    #     print(f"\t{my_addr}:{sock.getsockname()[1]}")

    # with (
    #     InboundWorker(sock, my_name, in_queue, user_list) as inbound_worker,
    #     OutboundWorker(sock, out_queue) as outbound_worker,
    # ):
    #     try:
    #         while True:
    #             sleep(1)
    #             for user in user_list:
    #                 out_queue.put((Sound(1), user.address))
    #     except KeyboardInterrupt:
    #         pass
    #     finally:
    #         del_user_message = DelUser(my_name)
    #         for user in user_list:
    #             print("Sending", del_user_message, "to", user.address)
    #             out_queue.put((del_user_message, user.address))


if __name__ == "__main__":
    main()
