from dataclasses import dataclass
from pickle import dumps, loads


@dataclass
class User:
    name: str
    address: str

    def serialize(self) -> bytes:
        return dumps(self)

    @staticmethod
    def deserialize(data: bytes) -> "User":
        return loads(data)
