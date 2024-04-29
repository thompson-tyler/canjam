# Project Final Report: Canjam

Roger Burtonpatel, Cece Crumlish, Skylar Gilfeather, Tyler Thompson

## Table of Contents

- [Project Final Report: Canjam](#project-final-report-canjam)
  - [Table of Contents](#table-of-contents)
  - [Design](#design)
  - [Outcome Analysis](#outcome-analysis)
  - [Design Reflection](#design-reflection)
    - [CanJam Canvas](#canjam-canvas)
    - [Peer to Peer Model](#peer-to-peer-model)
    - [Pygame Module (Cece and Roger)](#pygame-module-cece-and-roger)
  - [Division of Labor](#division-of-labor)
  - [Bug Report](#bug-report)
  - [Code Overview](#code-overview)
    - [Driver Script](#driver-script)
    - [Testing](#testing)


## Minimum Viable Project: Outcome and Analysis

The minimum functionality deliverables for CanJam required that CanJam be able
display unique colors and play unique synth sounds for each user interacting
with the canvas. This goal was achieved, although CanJam only supports four
different synth types, due to performance challenges in generating multiple
`pyfluidsynth` synth object at once. In the future, adapting the synth generation
process to use just one synth objects, or using a different sound generation
library entirely, could eliminate this bottleneck on the number of possible sounds.

Additionally, our minimum functionality deliverables for the larger CanJam
system design required that users be able to spin up a CanJam canvas
independently of any central server. In the CanJam peer-to-peer model, users
manage setup communications and share sound packets with their peers in a 
connected cluster of CanJam users. Our requirements outlined that CanJam
should support multiplayer clusters of minimally two users, and this was
achieved. However, because CanJam peers share sounds by unreliably broadcasting
large batches of small Sound packets, it was difficult to achieve the illusion
of continuously playing sound on the user end. On a user's local canvas,
this resulted in choppy sound and flickering color activation when displaying
a peer's activity on the canvas. However, despite this drawback, our testing
showed that at least six CanJam users could collaboratively play on the same
canvas with no increase in these performance issues when playing a peer's
incoming sounds.

Additional maximum functionality goals for CanJam involved generating animated
"trail" effects for user cursors on the canvas, varying sounds by timbre or
volume on the vertical axis of the grid, and playing a looping drum track
on each user canvas to serve as a metronome. While we were not able to achieve
any of these goals, they are all possible with the current libraries and
CanJam program infrastructure, and could be feasibly implemented with more time.

## Design Reflection

### CanJam Canvas
CanJam allows users to play music on a collaborative grid of notes. When clicking and holding, their current cell activates with their color and rings with its note. The barebones canvas GUI, a grid of music tiles, was designed to be intuitively playful and allow for freeform musical experimentation. Barring the latency issues in practice, the visual layout really gives users the convincing experience of playing sounds together on the same canvas.

The original MVP called for a grid with sounds that varied by pitch on the horizontal axis, and by volume on the vertical axis. Although the final MVP only varies notes by pitch, this proved to be a simpler musical interface: users can jump octaves by row, and glide across nodes by column. However, inconsistencies in the sound fonts used to generate synth notes made it difficult to create smooth pitch ranges. Some sound fonts are naturally pitched higher than others; which, in combination with a particularly large grid, result in the highest and lowest tiles generating inaudible pitches.   

Additionally, while the MVP describes users having their own unique color, users may have the same color or synth type, because no central server assigns specific colors and synth types to each user. Furthermore, the `CanJamSynth` module only supports a limited number of synth types, due to performance drawbacks of loading multiple sound font files into memory at once. Having "identical" users in a room isn't necessary a technical problem, although it may confuse other peers on the same canvas. To address this in the future, a user could potentially assign each of its neighboring peers a unique _relative_ color and sound. Or, peer clusters could deny new user requests from a user with a name already in the peer cluster user list.

### Peer to Peer Model
Furthermore, CanJam's peer-to-peer model, which lets users create freeform clusters of peers playing on the same canvas, allows CanJam a great deal of flexibility. While the peer-to-peer design was introduced as a fun pedagogical exercise, it ended up making multiplayer CanJam easy to initiate and resilient to individual failures. No central server is needed to spawn collaborative CanJam canvases, because each user runs their own CanJam instance independently. And, each CanJam user stores its own list of all its connected peers: so, users can spawn large-scale multiplayer canvases whenever they want. And, the peer-to-peer model also preserves CanJam canvases for remaining users when the founding member of the cluster has left. The peer-to-peer model wasn't chosen with the goal of handling expoentnial usership growth; but, on the other hand, it means that any user can create a multiplayer canvas whenever they want. 


### Pygame Module (Cece and Roger)

To be honest this module went through a lot of changes from the initial design. As we began to work more with pygame.

**One thing I feel particularly proud of is:** the inter-game process communication and getting everything to work in terms of updating the board visually with inbound sounds and sending outbound sounds to the correct modules. Additionally, having the game module abstracted from the process of joining a room and talking to other players was really helpful in getting everything to connect seamlessly, once the Peer-Peer portion was completed.

**One thing I wish I would have done differently though was to do more reading up on multiprocessing vs. multithreading:**

Initially I (Cece) thought it would be more beneficial and faster to use multiple processes with pygame as I thought it would allow for actual concurrency with the audio driver. But as it turns out inter-process communication is very slow and all the message passing and note playing on each process I was doing in that version was being hindered by how slow over the network communication was.

**If we had had more time:** I think we would have experimented with different concurrent solutions to the displaying multiple sounds at once problem we had. However we were so spread-thin with getting the pyfluidsynth and pygame to work, that we ran out of time, and didn't get to that part.

## Division of Labor

## Bug Report

## Code Overview

Code for the Canjam project is organized into three main directories:

1. The root directory, which contains the driver script `run.py`
2. The `canjam/` directory, which contains the bulk of the Canjam code
3. The `tests/` directory, which contains a number of unit test files which can be run using the instructions in the [testing](#testing) section

### Driver Script

The Canjam program is started by running `run.py`. It's purpose is to parse command line arguments and pass them off to the rest of the next entrypoint, the Canjammer.

The driver program accepts the following command line arguments:

1. `-n NAME, --name NAME`: The name to use when joining a room. This argument is required and the value should be a string.

2. `-j HOST:PORT, --join HOST:PORT`: Join a room by specifying the address of someone in the room. If not specified, a new empty room will be created. `HOST` must be a reachable IP address of someone in a Canjam room, and `PORT` is the port they're listening on.

3. `-p PORT, --port PORT`: The port to use for internet communication. If not specified, then one will be auto-assigned.

4. `-v, --verbose`: If this flag is present, Canjam will print more information to the console. This argument does not require a value.

### Testing

The `tests/` directory is a collection of scripts containing unit tests for various Canjam modules. As modules were implemented or their functionality changed, these tests were updates and run to ensure consistent behavior. Each test file is described below.

1. `test_canjamsynth.py` tests that the `CanJamSynth` module from `canjam/canjamsynth.py`. It ensures that a `CanJamSynth` object can be instantiated and used to play a note using a particular Fluidsynth synth type. Since it's very difficult to verify that the note was actually played, this test really just ensures that the constructor and `play_note` method don't crash.

2. `test_inboundworker.py` tests the `InboundWorker` module from `canjam/inboundworker.py`. It verifies that it functions correctly when receiving each type of message that is sent during Canjam operation. It ensures that the user list is mutated correctly and sounds are ferried to the `in_queue`. It also ensures that malformed messages are disregarded and do not crash the `InboundWorker.

3. `test_outboundworker.py` tests the `OutboundWorker` module from `canjam/outboundworker.py`. It verifies that messages are correctly formatted and sent to the appropriate destination. It also checks that the `OutboundWorker` handles errors gracefully without crashing. The tests cover different types of messages including sound, user list requests, user list responses, new user, and user deletion.

4. `test_user.py` tests the `User` module from `canjam/user.py`. It ensures that user objects can be correctly created and serialized. It also checks that the module correctly handles various edge cases, such as malformed user data.

5. `test_message.py` tests the `Message` module from `canjam/message.py`. It ensures that messages are correctly created, serialized, and deserialized. It also checks that the module correctly handles various edge cases, such as malformed messages.

6. `test_user.py` tests the `User` module from `canjam/user.py`. It verifies that user objects can be correctly created, serialized, and deserialized. It also checks that the module correctly handles various edge cases, such as malformed user data and serialization of many users with increasing name length and address. It also tests the deserialization of bad data, ensuring that it raises an exception as expected.
