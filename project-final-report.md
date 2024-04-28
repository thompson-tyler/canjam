# Project Final Report: Canjam

Roger Burtonpatel, Cece Crumlish, Skylar Gilfeather, Tyler Thompson

## Table of Contents

- [Project Final Report: Canjam](#project-final-report-canjam)
  - [Table of Contents](#table-of-contents)
  - [Design](#design)
  - [Outcome Analysis](#outcome-analysis)
  - [Design Reflection](#design-reflection)
  - [Division of Labor](#division-of-labor)
  - [Bug Report](#bug-report)
  - [Code Overview](#code-overview)
    - [Driver Script](#driver-script)
    - [Testing](#testing)

## Design

## Outcome Analysis

## Design Reflection

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

1. `-n|--name NAME`: The name to use when joining a room. This argument is required and the value should be a string.

2. `-j|--join HOST:PORT`: Join a room by specifying the address of someone in the room. If not specified, a new empty room will be created. `HOST` must be a reachable IP address of someone in a Canjam room, and `PORT` is the port they're listening on.

3. `-p|--port PORT`: The port to use for internet communication. If not specified, then one will be auto-assigned.

4. `-v|--verbose`: If this flag is present, Canjam will print more information to the console. This argument does not require a value.

### Testing

The `tests/` directory is a collection of scripts containing unit tests for various Canjam modules. As modules were implemented or their functionality changed, these tests were updates and run to ensure consistent behavior. Each test file is described below.

1. `test_canjamsynth.py` tests that the `CanJamSynth` module from `canjam/canjamsynth.py`. It ensures that a `CanJamSynth` object can be instantiated and used to play a note using a particular Fluidsynth synth type. Since it's very difficult to verify that the note was actually played, this test really just ensures that the constructor and `play_note` method don't crash.

2. `test_inboundworker.py` tests the `InboundWorker` module from `canjam/inboundworker.py`. It verifies that it functions correctly when receiving each type of message that is sent during Canjam operation. It ensures that the user list is mutated correctly and sounds are ferried to the `in_queue`. It also ensures that malformed messages are disregarded and do not crash the `InboundWorker.

3. `test_outboundworker.py` tests the `OutboundWorker` module from `canjam/outboundworker.py`. It verifies that messages are correctly formatted and sent to the appropriate destination. It also checks that the `OutboundWorker` handles errors gracefully without crashing. The tests cover different types of messages including sound, user list requests, user list responses, new user, and user deletion.

4. `test_user.py` tests the `User` module from `canjam/user.py`. It ensures that user objects can be correctly created and serialized. It also checks that the module correctly handles various edge cases, such as malformed user data.

5. `test_message.py` tests the `Message` module from `canjam/message.py`. It ensures that messages are correctly created, serialized, and deserialized. It also checks that the module correctly handles various edge cases, such as malformed messages.

6. `test_user.py` tests the `User` module from `canjam/user.py`. It verifies that user objects can be correctly created, serialized, and deserialized. It also checks that the module correctly handles various edge cases, such as malformed user data and serialization of many users with increasing name length and address. It also tests the deserialization of bad data, ensuring that it raises an exception as expected.
