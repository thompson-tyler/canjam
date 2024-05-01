# Canjam

Roger Burtonpatel, Cecelia Crumlish, Skylar Gilfeather, Tyler Thompson

## Installation Requirements

`canjam` requires Python >= 3.12. After cloning this repository, you'll need
to install the `FluidSynth` C library. Follow the instructions in the
[FluidSynth GitHub repository](https://github.com/FluidSynth/fluidsynth/wiki/Download#distributions) to install `FluidSynth` on your machine using your favorite package manager.

Then, you can install the `canjam` requirements via `pip3 install -r requirements.txt`.
On some machines, Python3.12 cannot find the C bindings for the FluidSynth library
when `CanJam` is run within a virtual environment. If this is the case, you'll
unfortunately have to install the following packages systemwide by appending
with the argument `--break-system packages`, i.e. `pip3 install -r requirements.txt --break-system packages`

```
pip3 install numpy
pip3 install pygame
pip3 install pyaudio
pip3 install pyfluidsynth
```

To run `canjam`, navigate to the root directory, `canjam`, and run `python3 run.py`.
The `canjam` executable takes the following arguments:

`-n / --name [NAME]`: Your displayed name to other CanJam peers.

`-j / --join [HOST:PORT]`: The hostname and port of another CanJam user,
to join their CanJam canvas.

`-p / --port [PORT]`: The port that your CanJam program should use for internet communication. If `-p` is not specified, the OS will assign you one.

`-v / --verbose`: Verbosity flag, to print debugging messages to the console.

## Code Overview

Code for the CanJam project is organized into three main directories:

1. The root directory, which contains the driver script `run.py`
2. The `canjam/` directory, which contains the bulk of the CanJam code
3. The `tests/` directory, which contains a number of unit test files which can be run using the instructions in the [testing](#unit-tests) section

### Driver Script

The CanJam program is started by running `run.py`. It's purpose is to parse command line arguments and pass them off to the rest of the next entrypoint, the CanJammer.

The driver program accepts the following command line arguments:

1. `-n NAME, --name NAME`: The name to use when joining a room. This argument is required and the value should be a string.

2. `-j HOST:PORT, --join HOST:PORT`: Join a room by specifying the address of someone in the room. If not specified, a new empty room will be created. `HOST` must be a reachable IP address of someone in a CanJam room, and `PORT` is the port they're listening on.

3. `-p PORT, --port PORT`: The port to use for internet communication. If not specified, then one will be auto-assigned.

4. `-v, --verbose`: If this flag is present, CanJam will print more information to the console. This argument does not require a value.

### The CanJam Modules

The CanJam Modules are all of the modules contained within the `canjam/` directory. They are used in concert to create the highly concurrent game, CanJam.

#### `canjammer`

The `canjam.canjammer` module provides the `CanJammer` class, which is a multi-threaded manager that oversees communications between the [`InboundWorker`](#inboundworker), [`OutboundWorker`](#outboundworker), and [`GameRunner`](#gamerunner) threads.

Key features of the `CanJammer` class include:

- It accepts command line arguments, such as the name to use when joining a room, the address of a room to join, the port to use for internet communication, and a verbosity flag.
- It initializes the shared server state, such as the list of connected users, and the shared [`JamSocket`](#jamsocket). If specified, it also bootstraps a connection with its first CanJam peer.
- It maintains a queue for inbound and outbound messages, and a set of connected users.

The `CanJammer` class is instantiated and run in the main function of the `run.py` script.

#### `gamerunner`

The `canjam.gamerunner` module provides the `GameRunner` class, which is responsible for running the CanJam game GUI using pygame. Key features of the `GameRunner` class include:

- It provides methods to draw the game grid and set the color of a grid cell.
- It uses a separate thread to handle sound messages from the `in_queue` and play the corresponding note on the [`CanJamSynth`](#canjamsynth) object.
- It maintains a queue for color flashes, which are used to animate the game grid when a note is played.
- It supports different player colors, which are randomly assigned when the `GameRunner` is initialized.

The `GameRunner` class is used by the [`CanJammer`](#canjammer) class to run the game GUI and handle sound messages from the `in_queue`.

#### `canjamsynth`

The `canjam.canjamsynth` module provides the `CanJamSynth` class, which is responsible for generating and playing sound data for the CanJam game. It uses the `numpy`, [`pyaudio`](https://people.csail.mit.edu/hubert/pyaudio/), and `fluidsynth` libraries to generate and play sounds. It provides a method to play a note, which generates the sound, plays it, and then stops the note. Multiple sound fonts are supported, which can be selected when creating an instance of the class.

The `CanJamSynth` class is used by the [`GameRunner`](#gamerunner) class to generate sound based on the game state.

#### `inboundworker`

The `canjam.inboundworker` module provides the `InboundWorker` class, a multi-threaded worker that listens for incoming messages on a [`Jamsocket`](#jamsocket) and processes them. [`Sound` messages](#message) are ferried to the `in_queue` to be consumed by a [`GameRunner`](#gamerunner), while all other messages are handled immediately by the worker, often mutating or sharing the user list with others.

#### `outboundworker`

The `canjam.outboundworker` module provides the `OutboundWorker` class, a multi-threaded worker that sends outgoing messages through a [`Jamsocket`](#jamsocket). It's quite a simple worker that sends [`Sound` messages](#message) unreliably and all other messages reliably.

#### `jamsocket`

The `canjam.jamsocket` module provides the `Jamsocket` class, a socket wrapper that provides both reliable and unreliable UDP communication methods.

Key features of the `Jamsocket` class include:

- It uses the [`socket`](https://docs.python.org/3/library/socket.html) library to create and manage a UDP socket.
- It provides methods to send and receive data, with optional reliability.
- It uses a separate thread that listens for incoming packets and handles timeouts for outstanding packets.
- It uses different types of packets, including `Ack`, `Data`, `DataNoAck`, `Skip`, `Die`, `Hello`, and `HelloAck` to send data and maintain connections with other `Jamsocket`s.

The `Jamsocket` class is used by the [`InboundWorker`](#inboundworker) and [`OutboundWorker`](#outboundworker) classes to send and receive messages over the network. `Sound` messages are sent unreliably to achieve low-latency, while all other messages are sent reliably to ensure a consistent room state.

Please note, that the packet types defined in the `jamsocket` module are _not_ the same as the [`message`](#message) types described below. The `jamsocket` packets are used internally by `jamsocket` to choreograph reliable message sending, while [`Message`](#message) objects are used by the [`InboundWorker`](#inboundworker), [`OutboundWorker`](#outboundworker), and [`GameRunner`](#gamerunner) to exchange user lists and sounds.

#### `badsocket`

The `canjam.badsocket` module provides a `badsocket` class that simulates a UDP socket with random network failures. It is a subclass of Python's built-in [`socket`](https://docs.python.org/3/library/socket.html) class and overrides some of its methods to introduce random failures. To prevent it from being used in a context that requires reliability, any attempts to use TCP-related methods like `connect`, `send`, `listen`, and `accept` will raise a `NotImplementedError`. It simulates random network failures in the `sendto` method. Sometimes it fails to send the packet, and other times it sends out withheld packets (to simulate duplicated packets).

#### `logger`

The `canjam.logger` module is a tiny module that allows a client to set verbosity, then use `vprint` to print messages only when verbose it set to true. `vprint` is used throughout CanJam to print out helpful debug messages when the game is run with the verbose (`-v`) flag.

#### `message`

The `canjam.message` module provides various classes representing different types of messages that can be sent over the network in the CanJam game. Each message type uses the [`dataclass`](https://docs.python.org/3/library/dataclasses.html) decorator which automatically generates a constructor that takes each field as arguments. Conveniently, each message class inherits from the `Message` class, which exists to provide `serialize` and `deserialize` methods. They use the [`pickle`](https://docs.python.org/3/library/pickle.html) module to convert to and from `bytes` representations of the messages. We probably could have designed smaller serialized representations of our messages, but [`pickle`](https://docs.python.org/3/library/pickle.html) is far more robust, so we deemed it worth the performance hit. Perhaps in a future version of CanJam it could serialize into a smaller custom scheme.

The `message` module is used by the [`InboundWorker`](#inboundworker), [`OutboundWorker`](#outboundworker), and [`CanJammer`](#canjammer) classes to send and receive CanJam-specific messages over the network.

#### `user`

The `canjam.user` module provides the `User` class, a data class representing a user in the CanJam game using their name and address. It's a tiny class that can serialize and deserialize instances of itself using [`pickle`](https://docs.python.org/3/library/pickle.html). Interestingly, it defines `__hash__` and `__eq__` implementation so it can be stored in a `set`, which is how the `user_set` is implemented.

### Unit Tests

The `tests/` directory is a collection of scripts containing unit tests for various CanJam modules. As modules were implemented or their functionality changed, these tests were updates and run to ensure consistent behavior. Each test file is described below.

1. `test_canjamsynth.py` tests that the [`CanJamSynth`](#canjamsynth) module from `canjam/canjamsynth.py`. It ensures that a [`CanJamSynth`](#canjamsynth) object can be instantiated and used to play a note using a particular Fluidsynth synth type. Since it's very difficult to verify that the note was actually played, this test really just ensures that the constructor and `play_note` method don't crash.

2. `test_inboundworker.py` tests the [`InboundWorker`](#inboundworker) module from `canjam/inboundworker.py`. It verifies that it functions correctly when receiving each type of message that is sent during CanJam operation. It ensures that the user list is mutated correctly and sounds are ferried to the `in_queue`. It also ensures that malformed messages are disregarded and do not crash the `InboundWorker.

3. `test_outboundworker.py` tests the [`OutboundWorker`](#outboundworker) module from `canjam/outboundworker.py`. It verifies that messages are correctly formatted and sent to the appropriate destination. It also checks that the [`OutboundWorker`](#outboundworker) handles errors gracefully without crashing. The tests cover different types of messages including sound, user list requests, user list responses, new user, and user deletion.

4. `test_user.py` tests the [`User`](#user) module from `canjam/user.py`. It ensures that user objects can be correctly created and serialized. It also checks that the module correctly handles various edge cases, such as malformed user data.

5. `test_message.py` tests the [`Message`](#message) module from `canjam/message.py`. It ensures that messages are correctly created, serialized, and deserialized. It also checks that the module correctly handles various edge cases, such as malformed messages.

6. `test_sockets.py` tests the [`Jamsocket`](#jamsocket) module. It constructs [`jamsocket`](#jamsocket)s using [`badsocket`](#badsocket) instances in order to simulate a terribly unreliable network, then sends many messages through the socket. There are even tests that spin up a bunch of threads to test the [`jamsocket`](#jamsocket)'s thread-safety! This is probably the most robust test file since it's absolutely imperative that the [`Jamsocket`](#jamsocket) functions well, otherwise many of the other mechanisms in other modules are not guaranteed.
