import unittest
from argparse import Namespace

from canjam.jamsocket import Jamsocket
from canjam.canjammer import CanJammer


class CanJammerTestCase(unittest.TestCase):

    def test_solo_canjammer(self):
        """Initialize a solo CanJam instance with no peers. Assert that its
        InboundWorker and OutboundWorker are processing incoming messages
        properly.
        """

        args = Namespace(name="skylar", join="127.0.0.1", port=1234, verbose=True)
        canjammer = CanJammer(args)
