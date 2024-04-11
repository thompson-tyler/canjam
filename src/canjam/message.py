from dataclasses import dataclass
from user import User


class Message:
    TID: bytes

    def serialize(self) -> bytes:
        return self.TID + self._serialize_data()

    def _serialize_data(self) -> bytes:
        raise NotImplementedError

    @staticmethod
    def deserialize(message: bytes) -> "Message":
        mid, data = message[0:1], message[1:]
        match mid:
            case Sound.TID:
                assert len(data) == Sound.DATA_SIZE
                return Sound(int.from_bytes(data, "big"))
            case ReqUserList.TID:
                assert len(data) == 0
                return ReqUserList()
            case RspUserList.TID:
                user_bytes_list = data.split(RspUserList.SERIAL_DELIM)
                user_list = [User.deserialize(user) for user in user_bytes_list]
                return RspUserList(user_list)
            case NewUser.TID:
                return NewUser(User.deserialize(data))
            case DelUser.TID:
                return DelUser(User.deserialize(data))
            case other:
                raise ValueError(f"Unknown message ID: {other.hex()}")


@dataclass
class Sound(Message):
    sound: int  # stub, replace with actual sound spec

    TID = b"\x01"
    DATA_SIZE = 4

    def _serialize_data(self) -> bytes:
        return self.sound.to_bytes(self.DATA_SIZE, "big")


@dataclass
class ReqUserList(Message):
    TID = b"\x02"

    def _serialize_data(self) -> bytes:
        return b""


@dataclass
class RspUserList(Message):
    user_list: list[User]

    TID = b"\x03"
    SERIAL_DELIM = b"\x00"

    def _serialize_data(self) -> bytes:
        return self.SERIAL_DELIM.join(
            user.serialize() for user in self.user_list
        )


@dataclass
class NewUser(Message):
    user: User

    TID = b"\x04"

    def _serialize_data(self) -> bytes:
        return self.user.serialize()


@dataclass
class DelUser(Message):
    user: User

    TID = b"\x05"

    def _serialize_data(self) -> bytes:
        return self.user.serialize()
