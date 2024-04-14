from random import random
from socket import AddressFamily, SocketKind, socket


FAIL_RATE = 0.2


class badsocket(socket):
    """
    A socket wrapper class that can only be used as a UDP socket.
    It provides proxy methods that simulate random network failures.
    """

    def __init__(self, family: AddressFamily, kind: SocketKind):
        self.__withheld = []
        super().__init__(family, kind)

    def sendto(self, data, address):
        # If sending to self, just send the packet normally to simulate a local network
        local = self.getsockname() == address
        if local:
            return super().sendto(data, address)

        # Sometimes send out withheld packets
        if self.__withheld and random() > FAIL_RATE:
            for data_, address_ in self.__withheld:
                super().sendto(data_, address_)
            self.__withheld.clear()

        # Sometimes fail to send the packet
        if random() < FAIL_RATE:
            return len(data)

        # # Sometimes queue the packet to be sent later
        # if random() < FAIL_RATE:
        #     self.__withheld.append((data, address))

        return super().sendto(data, address)

    # Disallow TCP related methods
    def connect(self, address):
        raise NotImplementedError("Illegal op, this socket is UDP only")

    def send(self, data):
        raise NotImplementedError("Illegal op, this socket is UDP only")

    def listen(self):
        raise NotImplementedError("Illegal op, this socket is UDP only")

    def accept(self):
        raise NotImplementedError("Illegal op, this socket is UDP only")
