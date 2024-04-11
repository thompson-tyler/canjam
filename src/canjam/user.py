from dataclasses import dataclass


@dataclass
class User:
    name: str
    address: str

    SERIAL_DELIM = b":"

    def serialize(self) -> bytes:
        return self.name.encode() + self.SERIAL_DELIM + self.address.encode()

    @staticmethod
    def deserialize(data: bytes) -> "User":
        name, address = data.split(b":")
        return User(name.decode(), address.decode())
