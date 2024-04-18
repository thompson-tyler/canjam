from dataclasses import dataclass
from socket import AF_INET, SOCK_DGRAM, socket
from threading import Thread, Semaphore, Lock
from time import time
from pickle import dumps, loads
from random import random
from queue import Queue


# The amount of time jamsocket will wait for an ack before resending a packet, in seconds
ACK_TIMEOUT = 0.1

# The number of times jamsocket will resend a packet before giving up
MAX_RESENDS = 50

# A handy type alias for an address tuple - a host address and a port
address = tuple[str, int]

uuid = int


@dataclass
class Ack:
    """
    An ack packet that is sent to acknowledge a received packet. This
    packet contains the id of the connection and the sequence number of the
    packet that is being acknowledged.
    """

    id_: uuid
    seq: int


@dataclass
class Data:
    """
    A data packet that is sent to reliably transmit data. This packet
    contains the id of the connection, the sequence number of this packet,
    and the data to be transmitted.
    """

    id_: uuid
    seq: int
    data: bytes


@dataclass
class DataNoAck:
    data: bytes


@dataclass
class Skip:
    pass


@dataclass
class Die:
    pass


@dataclass
class Hello:
    id_: uuid


@dataclass
class HelloAck:
    id_: uuid


jampacket = Ack | Data | DataNoAck | Skip | Die | Hello | HelloAck


@dataclass
class Connection:
    """
    A connection between two hosts, generated by a hello/hello_ack
    handshake. The id_ value is shared between the two hosts and is agreed
    upon during the handshake. The seq_counter is the next sequence number
    that we will use when sending to the address. The expected_seq is the
    next sequence number that we expect to receive from the address.
    """

    id_: uuid
    peer: address
    seq_counter: int = 0
    expected_seq: int = 0


@dataclass
class OutstandingPacket:
    """
    A packet that has been sent and is waiting for an ack.
    """

    conn: Connection
    seq: int  # The sequence number of this packet
    time_sent: float
    data: bytes
    ack_received: Semaphore
    resends: int = 0

    def into_packet(self) -> jampacket:
        raise NotImplementedError

    def is_hello(self):
        return isinstance(self, OutstandingHello)


class OutstandingData(OutstandingPacket):
    def into_packet(self):
        return Data(self.conn.id_, self.seq, self.data)


class OutstandingHello(OutstandingPacket):
    def into_packet(self):
        return Hello(self.conn.id_)


class Jamsocket:
    """
    A socket wrapper that provides both reliable and unreliable UDP
    communication methods
    """

    # The underlying socket which jamsocket wraps
    __sock: socket
    # A list of packets that this socket has sent and will periodically resend
    # until an ack is received
    __needs_ack: list[OutstandingPacket]
    # As the inbox worker receives new data packets, it adds them here for
    # readers to pick up. Each item in the list is a tuple of the data and the
    # source address
    __inbox: Queue[tuple[bytes, address]]
    # A semaphore that readers can wait on to be notified when a new packet is
    # available in the inbox
    __inbox_has_item: Semaphore
    __inbox_worker_thread: Thread
    # A list of active connections to other clients
    __connections: list[Connection]
    __connections_lock: Lock

    def __init__(
        self,
        port: int,
        socket_type: type[socket] = socket,
    ):
        self.__sock = socket_type(AF_INET, SOCK_DGRAM)
        self.__needs_ack = []
        self.__inbox = Queue()
        self.__inbox_has_item = Semaphore(0)
        self.__inbox_worker_thread = Thread(target=self.__inbox_worker)
        self.__connections = []
        self.__connections_lock = Lock()

        try:
            # Binding to 0.0.0.0 allows us to receive packets from any address
            self.__sock.bind(("0.0.0.0", port))
        except PermissionError:
            raise PermissionError(
                f"Permission denied to bind to port {port}. Try running the "
                + "program as an administrator or using a different port."
            )
        self.__inbox_worker_thread.start()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def __del__(self):
        self.close()

    def __inbox_worker(self):
        while True:
            # Check on all packets that need to be acked
            # If a packet has been resent too many times, remove it from the
            # list and release the ack semaphore
            # If a packet has been waiting too long for an ack, resend it
            now = time()
            for packet in self.__needs_ack:
                if packet.resends >= MAX_RESENDS:
                    packet.data = b""
                    packet.ack_received.release()
                    self.__needs_ack.remove(packet)
                elif now - packet.time_sent > ACK_TIMEOUT:
                    data_packet = packet.into_packet()
                    self.__sock.sendto(dumps(data_packet), packet.conn.peer)
                    packet.time_sent = now
                    packet.resends += 1

            # If there are packets that need to be acked, set the timeout to
            # the next ack timeout
            if self.__needs_ack:
                oldest_sent = min(map(lambda p: p.time_sent, self.__needs_ack))
                timeout = max(oldest_sent + ACK_TIMEOUT - now, 0)
                self.__sock.settimeout(timeout)
            else:
                self.__sock.settimeout(None)

            # Receive a packet
            try:
                data, from_address = self.__sock.recvfrom(4096)
                new_packet: jampacket = loads(data)
                self.__handle_packet(new_packet, from_address)
            except TimeoutError:
                continue

    def __handle_packet(self, packet: jampacket, from_address: address):
        # Deserialize the packet and match on it
        match packet:
            case Ack(id_, seq):
                # Find packets that this ack applies to
                out_packets = self.__matching_out_packets(id_, seq)
                assert len(out_packets) <= 1
                for out_pack in out_packets:
                    out_pack.ack_received.release()
                    self.__needs_ack.remove(out_pack)
            case Data(id_, seq, data):
                # Get the connection object for this packet
                conn = self.__conn_by_id(id_)

                # If the connection doesn't exist, drop this packet
                if conn is None:
                    return

                # Send an ack for the received packet if it's the expected
                # packet or a previous packet
                if seq <= conn.expected_seq:
                    ack_pack = Ack(id_, seq)
                    self.__sock.sendto(dumps(ack_pack), from_address)

                # If the packet is the next expected packet, add it to the
                # inbox and increment the expected sequence number
                if seq == conn.expected_seq:
                    self.__inbox.put((data, from_address))
                    self.__inbox_has_item.release()
                    conn.expected_seq += 1
            case DataNoAck(data):
                # Add the packet to the inbox. No ack is needed for this packet
                # type
                self.__inbox.put((data, from_address))
                self.__inbox_has_item.release()
            case Skip():
                pass
            case Die():
                # Kill the inbox worker thread
                raise SystemExit
            case Hello(id_):
                with self.__connections_lock:
                    # If we have a connection from this address with a different id,
                    # remove it. This occurs when the peer has restarted and is
                    # trying to connect to us again
                    existing = self.__conn_by_address(from_address)
                    if existing and existing.id_ != id_:
                        self.__connections.remove(existing)

                    # If this is a new connection id, create a new connection
                    existing = self.__conn_by_id(id_)
                    if not existing:
                        conn = Connection(id_, from_address)
                        self.__connections.append(conn)

                # Send an ack back to the sender
                ack = HelloAck(id_)
                self.__sock.sendto(dumps(ack), from_address)
            case HelloAck(id_):
                # Find the outstanding hello packet for this ack, and drop it if
                # it doesn't exist
                hello_packet = next(
                    (
                        packet
                        for packet in self.__needs_ack
                        if packet.is_hello() and packet.conn.id_ == id_
                    ),
                    None,
                )
                if hello_packet is None:
                    return

                # Remove the hello packet from the needs_ack list
                self.__needs_ack.remove(hello_packet)

                with self.__connections_lock:
                    # Remove any existing connections to this address
                    existing = self.__conn_by_address(from_address)
                    if existing:
                        self.__connections.remove(existing)

                    # Add the new connection to the connections list
                    self.__connections.append(hello_packet.conn)

                # Wake up any threads waiting for this connection to be
                # established
                hello_packet.ack_received.release()
            case other:
                raise ValueError(f"Unknown packet: {other}")

    def __matching_out_packets(self, id_: float, seq: int):
        return [
            packet
            for packet in self.__needs_ack
            if packet.conn.id_ == id_ and packet.seq == seq
        ]

    # Returns a connection object if one exists, otherwise None
    def __conn_by_id(self, id_: uuid):
        return next(
            (conn for conn in self.__connections if conn.id_ == id_), None
        )

    # Returns a connection object if one exists, otherwise None
    def __conn_by_address(self, addr: address):
        return next(
            (conn for conn in self.__connections if conn.peer == addr), None
        )

    def __put_skip(self):
        self.__sock.sendto(dumps(Skip()), self.__sock.getsockname())

    def connect(self, dest: address):
        """
        Establishes a connection with the destination address. A client at the
        destination must be running a jamsocket, and this method must be called
        before sending them any data. This method blocks until the connection is
        established. If the connection cannot be established, an OSError is
        raised. If a connection to the destination has already been established,
        this method will re-establish the connection.
        """
        # Instantiate a new connection object and add it to the connections list
        with self.__connections_lock:
            conn = Connection(int(random() * 2**32), dest)
            # Remove existing connections to this address
            existing = self.__conn_by_address(dest)
            if existing:
                self.__connections.remove(existing)

        # Instantiate a new outstanding hello packet, add it to the needs_ack
        # list, and send the hello packet
        out_packet = OutstandingHello(conn, 0, time(), b"", Semaphore(0))
        hello_packet = out_packet.into_packet()
        self.__needs_ack.append(out_packet)
        self.__sock.sendto(dumps(hello_packet), dest)
        self.__put_skip()

        # Wait for the hello_ack
        out_packet.ack_received.acquire()

        # Check whether the connection was established, and raise an error if
        # it wasn't
        if self.__conn_by_address(dest) is None:
            raise OSError(
                f"Timeout establishing connection to {dest}, from {self.__sock.getsockname()}"
            )

    def close(self):
        """
        Closes the socket and stops internal threads. This method must be called
        before exiting the program to avoid a hang.
        """
        # Send a die packet to the inbox worker thread to tell it to stop
        # Is this... message passing..?
        if self.__inbox_worker_thread.is_alive():
            self.__sock.sendto(dumps(Die()), self.__sock.getsockname())
            self.__inbox_worker_thread.join()
        # Close the socket if it's still open
        if self.__sock.fileno() != -1:
            self.__sock.close()

    def sendto_unreliably(self, data: bytes, dest: address):
        """
        Sends data to the destination address and returns the length of the data
        that was sent. If a bad address is provided, an OSError is raised. Makes
        no guarantees about the delivery of the packet. Non-blocking.
        """
        packet = DataNoAck(data)
        self.__sock.sendto(dumps(packet), dest)
        return len(data)

    def sendto_reliably(self, data: bytes, dest: address):
        """
        Sends data to the destination address and blocks until an ack is
        received. Returns the length of the data that was sent. If too many
        resends occur without an ack, we assume that the host is down and return
        0. If a bad address is provided, an OSError is raised.
        """
        # Get the connection object for this destination
        with self.__connections_lock:
            conn = self.__conn_by_address(dest)
            if conn is None:
                raise OSError(
                    "Connection to the destination address does not exist. "
                    + f"Consider calling connect({dest}) first."
                )

            # Acquire the next sequence number for this particular destination
            # and increment the sequence counter
            seq = conn.seq_counter
            conn.seq_counter += 1

        # Construct an outstanding packet for this message, add it to the
        # needs_ack list, and send the data packet
        out_packet = OutstandingData(conn, seq, time(), data, Semaphore(0))
        data_packet = out_packet.into_packet()
        self.__needs_ack.append(out_packet)
        self.__sock.sendto(dumps(data_packet), dest)
        self.__put_skip()

        # Wait until an ack is received, and then return the length of the data.
        # Note that the data field may have been set to an empty byte string to
        # indicate that the packet was not successfully delivered, in which case
        # returning 0 indicates that the data was not sent
        out_packet.ack_received.acquire()
        return len(out_packet.data)

    def sendto_self(self, data: bytes):
        """
        Sends data to the local host. Returns the length of the data that was
        sent.
        """
        return self.sendto_unreliably(data, self.__sock.getsockname())

    def recvfrom(self, timeout: float | None = None):
        """
        Blocks until a datagram is available in the buffer, then returns the
        data and the source address as a tuple (data, address). If a timeout is
        provided and no data is available after that time, a TimeoutError is
        raised.
        """
        success = self.__inbox_has_item.acquire(timeout=timeout)
        if not success:
            raise TimeoutError
        return self.__inbox.get()

    def recv(self, timeout: float | None = None):
        """
        Blocks until a datagram is available in the buffer, then returns the
        data. If a timeout is provided and no data is available after that time,
        a TimeoutError is raised.
        """
        data, _ = self.recvfrom(timeout)
        return data

    def getsockname(self):
        """
        Returns the address of the socket.
        """
        return self.__sock.getsockname()
