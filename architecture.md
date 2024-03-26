# CanJam Architecture

## Classes

![UML diagram](https://www.mermaidchart.com/raw/f6dcf7b0-ed29-4cbc-b0ed-951bd717cdd1?theme=dark&version=v0.1&format=svg)

- `User`
  - `name`: string
  - `address`: the users address
- `TSocket`
  - A monitor wrapper for a UDP socket
- `TQueue`
  - A monitor wrapper for a queue data structure
- `OutboundJob` = `tuple(Message, list(User))`
  - A job for the outbound worker
  - A product type of recipient users and the message to send to them
- `Message` = `Sound` | `GetUserList` | `UserList` | `NewUser` | `ByeUser`
  - A summation type of various message [dataclasses](https://docs.python.org/3/library/dataclasses.html)
- `Sound`
  - A dataclass with the following members:
    - `sound`: int (?)
    - `duration`: int (?)
  - The message type when a user is sending a sound to another user
  - Members have not been fully fleshed out yet
- `GetUserList`
  - The message type when a user requests the user list from another user
- `UserList`
  - A dataclass with the following member:
    - `users`: `list(User)`
  - The message type in response to a `GetUserList` message
- `NewUser`
  - A dataclass with the following member:
    - `user`: `User`
  - The message type when a user wants to notify another user that it's entering a room, adding it to the recipient's user list
- `ByeUser`
  - A dataclass with the following member:
    - `user`: `User`
  - The message type when a user wants to indicate that they're leaving the room, removing themselves from the recipient's user list

## Objects

![Object diagram](https://www.mermaidchart.com/raw/68592021-392a-460e-9b57-6e242a03cfdf?theme=light&version=v0.1&format=svg)

- Main thread is running Pygame loop
  - Checks for user input, clicking tiles, exiting, leaving rooms, etc.
  - When the user performs an action that must be communicated to the other users, it adds it to the `out_queue` as an `OutboundJob` instance
- Outbound Worker
  - Waits for events to come in on the `out_queue`
  - Converts those events to byte streams and sends them to the recipient users
- Inbound Worker
  - Waits for data from other users on the `com_sock`
  - Interprets that data, producing a relevant sound event, and pushes it to the `in_queue`
  - If the data is not a sound event, it will be handled immediately and a response may be pushed to the `out_queue`
  - The `user_list` may be read or written to depending on the message type

### Shared Mutable Data

- `out_queue`: `TQueue(OutboundJob)`
  - Outbound message queue
- `in_queue`: `TQueue(Sound)`
  - Inbound sound queue
- `user_list`: `list(User)`
  - A list of all the other users in the current room
- `user_list_lock`: `Lock`
  - We may need this lock for the `user_list`
- `com_sock`: `TSocket`
  - A UDP socket that's used for communication with other users
  - The inbound consumer thread listens on this socket for sounds, new connections, etc.
  - The outbound consumer and similar outbound threads use this to send data to other users
