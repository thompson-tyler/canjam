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


if __name__ == "__main__":
    game_runner = GameRunner(Queue(), Queue())
    game_runner.run_game()
