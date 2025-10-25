from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    password: str
    is_moderator: bool

    @classmethod
    def from_row(cls, data: dict):
        return cls(
            id=data["id"],
            name=data["name"],
            password=data["password"],
            is_moderator=data["is_moderator"],
        )
