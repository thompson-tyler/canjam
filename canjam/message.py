from dataclasses import dataclass
from pickle import dumps, loads

from canjam.user import User


class Message:
    def serialize(self) -> bytes:
        return dumps(self)

    @staticmethod
    def deserialize(message: bytes) -> "Message":
        return loads(message)


@dataclass
class Sound(Message):
    sound: int  # stub, replace with actual sound spec


@dataclass
class ReqUserList(Message):
    pass


@dataclass
class RspUserList(Message):
    user_list: list[User]


@dataclass
class NewUser(Message):
    user: User


@dataclass
class DelUser(Message):
    user: User