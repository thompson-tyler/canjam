# Project Final Report: Canjam

Roger Burtonpatel, Cece Crumlish, Skylar Gilfeather, Tyler Thompson

## Table of Contents

- [Project Final Report: Canjam](#project-final-report-canjam)
  - [Table of Contents](#table-of-contents)
  - [Project Proposal](#project-proposal)
    - [Minimum Deliverables](#minimum-deliverables)
    - [Maximum Deliverables](#maximum-deliverables)
    - [Foreseeable challenges](#foreseeable-challenges)
    - [First Step](#first-step)
  - [Design](#design)
  - [Outcome Analysis](#outcome-analysis)
  - [Design Reflection](#design-reflection)
    - [Pygame Module (Cece and Roger)](#pygame-module-cece-and-roger)
  - [Division of Labor](#division-of-labor)
  - [Bug Report](#bug-report)
  - [Code Overview](#code-overview)
    - [Driver Script](#driver-script)
    - [Testing](#testing)

## Project Proposal

We propose the game **CanJam**.

**CanJam** is a multiplayer melody maker that allows users to play music with each other across multiple laptop instances. We were inspired by the Chrome Music Lab Melody Maker. Our goal with this project is to build a fun, colorful and fun-to-play visual interface, including different musical instruments.

### Minimum Deliverables

1. Basic Sound Modulation and playback via Pyaudio using the Pyfluidsynth library.
2. Tiles that sound varying in pitch, no vertical volume or timbre axis.
3. Single instrument sound type available.
4. Users are assigned a default color and the user's active tile is highlighted with color.
5. Users Play peer sounds as soon as they arrive with no conception of preserving accurate time delay from network delay.
6. Users capable of playing the game with themselves, and connecting to each other's sessions over a Peer-peer server.
7. `<=` 4 users in a single room.

### Maximum Deliverables

1. `>` 4 players in a room.
2. Visual noise animations, like sparkles, or explode on the grid.
3. More modulators added, such as timbre and volume.
4. More instruments loaded in.
5. A globally looping drum track.

### Foreseeable challenges

One of the biggest foreseeable challenges with this project is getting the synths to play nice and work together. As we saw in our initial experiments, playing different synths on the same computer will require some switching between modules and maneuvering handled by the audio driver which may prove to be a limiting factor in the amount of different instruments playing in a single room that we will be able to support at a given time.  

### First Step

Get the music GUI to work: support mouse-over activation of a tiled grid of buttons that each play a note from a particular soundfont loaded onto a synth object by the CanJamSynth module.

This was the logical first step for our project since pygame and playing sounds was the most foreign, mysterious piece of the project. We wanted to make sure it was all possible before proceeding with the rest of the project.

## Design

## Outcome Analysis

## Design Reflection

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
