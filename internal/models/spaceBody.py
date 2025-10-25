from dataclasses import dataclass


@dataclass
class SpaceBody:
    id: int
    name: str
    is_visible: bool
