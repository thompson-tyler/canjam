from dataclasses import dataclass
from pickle import dumps, loads
from canjam.jamsocket import address


@dataclass
class User:
    name: str
    address: address

    def serialize(self) -> bytes:
        return dumps(self)

    @staticmethod
    def deserialize(data: bytes) -> "User":
        return loads(data)

    def __hash__(self) -> int:
        return hash(self.name + str(self.address))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.name == other.name and self.address == other.address
