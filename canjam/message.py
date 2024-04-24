from dataclasses import dataclass
from pickle import dumps, loads
from enum import Enum

from canjam.user import User
from canjam.sound_fonts.canjamsynth import SynthType


class Message:
    def serialize(self) -> bytes:
        return dumps(self)

    @staticmethod
    def deserialize(message: bytes) -> "Message":
        m = loads(message)
        if not isinstance(m, Message):
            raise ValueError("Deserialized object is not a Message")
        return m

class Color(Enum):
    STRAWB = (249, 65, 68)
    ORANGE = (243, 114, 44)
    HONEY = (249, 199, 79)
    MATCHA = (144, 190, 109)
    MINT = (67, 170, 139)
    BLUEB = (87, 117, 144)

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)

@dataclass
class Cell():
    coords: tuple[int, int]
    color: Color

@dataclass
class Sound(Message):
    note: int
    color: Color
    synth_type: SynthType


@dataclass
class ReqUserList(Message):
    pass


@dataclass
class RspUserList(Message):
    source_name: str
    user_list: set[User]


@dataclass
class NewUser(Message):
    name: str


@dataclass
class DelUser(Message):
    name: str


@dataclass
class Die(Message):
    pass


@dataclass
class Die(Message):
    pass
