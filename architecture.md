# CanJam Architecture

- Need outbound events to be added to an outbound buffer
- Inbound events added to an inbound buffer, which is then consumed by pygame

## Classes

- `User`
  - `name`: string
  - `address`: the users address
- `Event` a [dataclass](https://docs.python.org/3/library/dataclasses.html) that encodes information about an event. This can be a sound, a request for the user list, a new user broadcast
  - `SoundEvent` | `UserList` | `NewUser`
- `SoundEvent`

## Objects

- Main thread is running Pygame loop
  - Checks for user input, clicking tiles, exiting, leaving rooms, etc.
  - When the user performs an action that must be communicated to the other users, it adds it to the `out_queue` as an event object
- Outbound Consumer
  - Waits for events to come in on the `out_queue`
  - Converts those events to byte streams and broadcasts them to all users in the `user_list`
- Inbound Consumer
  - Waits for data on the `com_sock`
  - Interprets that data, producing a relevant sound event, and pushes it to the `in_queue`
  - If the data is

### Shared Mutable Data

- `out_queue`
  - Outbound event queue
- `in_queue`
  - Inbound event queue
- `user_list`: `list(User)`
  - A list of all the other users in the current room
- `com_sock`
  - A UDP socket that's used for communication with other users
  - The inbound consumer thread listens on this socket for sounds, new connections, etc.
  - The outbound consumer and similar outbound threads use this to send data to other users
- `com_sock_lock`
  - A lock for the `com_sock`
